import xml.etree.ElementTree
import os
import csv
from pprint import pprint


class CrlMarcXML:
    """
    Converts MARCXML to one or more text MARC records.
    Single record conversion will be for OCLC searches, and other searches that
    can only ever return a single record. Note that an SRU search can always 
    in theory return more than one record, so those must use the list function.

    usage:
        cmx = CrlMarcXML()
        list_of_marc_records = cmx.marcxml_to_marc(xml_string)
        single_marc_as_string = cmx.marcxml_to_single_record(xml_string)

    """

    def __init__(self, log_file='marcxml_issues.log', log_results=False):
        self.log_file = log_file
        self.log_results = log_results
        self.printed_log_header = False
        self._delete_old_log_file()
        self.xml = None
        self.marc_records = None
        self.record_count = 0

    def _delete_old_log_file(self):
        try:
            os.remove(self.log_file)
        except FileNotFoundError:
            pass

    def _print_issue_to_log(self, issue_message_list):
        if not self.log_results:
            return
        if not self.printed_log_header:
            self._print_log_header()
        fout = open(self.log_file, 'a', encoding='utf8')
        fout.write('{}\n'.format(issue_message_list))
        fout.close()

    def _print_log_header(self):
        fout = open(self.log_file, 'w', encoding='utf8')
        cout = csv.writer(fout, delimiter='\t')
        cout.writerow(['record_count', 'field', 'subfield', 'issue'])
        fout.close()
        self.printed_log_header = True

    def marcxml_to_marc(self, xml_input):
        """
        converts MARCXML to MARC record(s)
        """
        self.xml = xml_input
        self.marc_records = []
        root = xml.etree.ElementTree.fromstring(self.xml)
        self._process_child(root)
        return self.marc_records

    def marcxml_text_file_to_marc(self, xml_input_file):
        with open(xml_input_file, 'r', encoding='utf8') as fin:
            xml_string = [l.rstrip() for l in fin]
        marc_records = self.marcxml_to_marc(xml_string)
        return marc_records

    def _process_child(self, child):
        """
        recurse through children in the XML tree.
        when one looks like an individual Marc record, send it along for conversion to text.
        """
        if '{http://www.loc.gov/MARC21/slim}record' in child.tag:
            self.record_count += 1
            mrk_record = self.marcxml_to_single_record(child)
            if mrk_record:
                self.marc_records.append(mrk_record)
        else:
            for sub_child in child:
                self._process_child(sub_child)

    def marcxml_to_single_record(self, child):
        """
        convert and individual Marc record's worth of XML to text, and add it to the output list.
        """
        this_marc_record_list = []
        for field_data in child:
            field = self._make_field(field_data)
            if field:
                this_marc_record_list.append(field)
        if this_marc_record_list:
            mrk_record = "\n".join(this_marc_record_list)
            return mrk_record

    def _make_field(self, field_data):
        """
        single field to single line of a Marc record
        """
        if "leader" in field_data.tag:
            field = "=LDR  {}".format(field_data.text) 
            return field
        field_number = field_data.attrib["tag"]
        if 'controlfield' in field_data.tag:
            field_text = field_data.text.replace(" ", "\\")
            return "={}  {}".format(field_number, field_text)
        ind1 = field_data.attrib["ind1"]
        ind2 = field_data.attrib["ind2"]
        ind1 = ind1.replace(" ", "\\")
        ind2 = ind2.replace(" ", "\\")
        field = "={}  {}{}".format(field_number, ind1, ind2)
        for subfield_data in field_data:
            subfield_code = subfield_data.attrib["code"]
            subfield_text = subfield_data.text
            if not subfield_text:
                issue_message_list = [self.record_count, field_number, subfield_code, 'Blank subfield']
                self._print_issue_to_log(issue_message_list)
                continue

            subfield_text.replace("$", "{dollar}")

            field = "{}${}{}".format(field, subfield_code, subfield_text)
        return field
