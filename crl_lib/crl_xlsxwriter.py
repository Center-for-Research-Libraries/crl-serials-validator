import xlsxwriter
import statistics
import math
from termcolor import colored


class CRLXlsxWriter:
    def __init__(self, workbook_name, worksheet_names_and_data, header=True, freeze_top_row=True) :
        """
        worksheet_names_and should be a dict (or preferably OrderedDict) of names to a list of list rows containing
        output and a list for any columns that should be treeated as numbers. Something like:

            OrderedDict = {"first_sheet_name": 
                                {"data": [["A1", "B1", "C1"], ["A2", "B2", "C2"]],
                                "number_columns" : [0, 2],
                                "special_formats": [({'bold': True, 'bg_color': '#D8D8D8'}, [0, 15, 16]),
                                                    ({'bg_color': '#FF000'}, [17, 22])]},
                           "second_sheet_name":
                               {"data": [["A1", "B1", "C1"], ["A2", "B2", "C2"]],
                                "number_columns" : [],
                                "special_formats": special_format_tuples}
                            }
        special_format_tuples should be tuples with two values, the first being an xlsxwriter format dict (something
        like "{'bold': True, 'bg_color': '#D8D8D8'}"), the second being a list or tuple of all of the rows in which that
        format should be used. Only one special format should be applied to every row. If more than one is assigned to
        a row then the later one will override the earlier.

        Setting header to True will cause the first row to be printed entirely as strings.
        """
        cprint('Creating workbook {}'.format(colored(workbook_name), 'cyan'))
        self.workbook = xlsxwriter.Workbook(workbook_name)

        # To force a cell to be treated as text by xlsxwriter need to set 'num_format' to '@'.
        text_format = self.workbook.add_format({'num_format': '@'})
        for worksheet_name in worksheet_names_and_data:
            number_columns = set()
            if "number_columns" in worksheet_names_and_data[worksheet_name]:
                for column_number in worksheet_names_and_data[worksheet_name]["number_columns"]:
                    number_columns.add(column_number)

            standard_format = self.workbook.add_format({'text_wrap': True})
            # Default is a basic bold-faced header. This can be overridden with a special_format_tuple.
            special_formats = {
                "bold": self.workbook.add_format({'bold': True, 'text_wrap': True}),
            }
            special_format_rows = {
                0: "bold"
            }
            try:
                special_format_number = 0
                for special_format_tuple in worksheet_names_and_data[worksheet_name]["special_formats"]:
                    special_format, format_rows = special_format_tuple
                    special_formats[special_format_number] = self.workbook.add_format(special_format)
                    for format_row in format_rows:
                        special_format_rows[format_row] = special_format_number
                    special_format_number += 1
            except KeyError:
                pass
            # if len(worksheet_name) > 30:
            #     worksheet = self.workbook.add_worksheet(worksheet_name[:20] + '...' + worksheet_name[-5:-1])
            # else:
            worksheet = self.workbook.add_worksheet(worksheet_name[:30])
            if freeze_top_row is True:
                worksheet.freeze_panes(1, 0)
            worksheet_column_widths = self.get_column_info(worksheet_names_and_data[worksheet_name]["data"])
            for i in range(0, len(worksheet_column_widths)):
                worksheet.set_column(i, i, width=worksheet_column_widths[i])
            row = 0
            for output_row in worksheet_names_and_data[worksheet_name]["data"]:
                if row in special_format_rows:
                    row_format = special_format_rows[row]
                    worksheet.set_row(row, None, special_formats[row_format])
                else:
                    worksheet.set_row(row, None, standard_format)

                column = 0
                for output_cell in output_row:
                    if row == 0 and header is True:
                        worksheet.write_string(row, column, str(output_cell))
                    elif not output_cell:
                        worksheet.write_blank(row, column, None)
                    elif column in number_columns:
                        try:
                            output_data = int(output_cell)
                            worksheet.write_number(row, column, output_data)
                        except ValueError:
                            worksheet.write_string(row, column, str(output_cell))
                    else:
                        worksheet.write_string(row, column, str(output_cell), text_format)
                    column += 1
                row += 1
            # apply word wrap to everything
        self.workbook.close()

    @staticmethod
    def get_column_info(input_grid):
        """
        Find appropriate widths for every column.
        """
        total_column_widths = []
        output_column_widths = []
        for row in input_grid:
            # used_row = False
            col = 0
            for cell in row:
                try:
                    total_column_widths[col]
                except IndexError:
                    total_column_widths.append(list())
                if len(str(cell)) >= 1:
                    total_column_widths[col].append(len(str(cell)))
                col += 1

        for i in range(0, len(total_column_widths)):
            col_list = total_column_widths[i]
            if len(col_list) == 1:
                # to get around statistics error when column only has a header
                col_list.append(col_list[0])
            mean = statistics.mean(col_list)
            stdev = statistics.stdev(col_list)
            length = math.ceil(mean + stdev) + 2
            # if width is narrower than header, set to width of header
            if length < len(str(input_grid[0][i])):
                length = len(str(input_grid[0][i]))
            if length > 60:
                length = 60
            output_column_widths.append(length)
        return output_column_widths
