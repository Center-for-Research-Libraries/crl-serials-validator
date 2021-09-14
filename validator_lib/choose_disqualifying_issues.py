"""
Class to allow the user to decide that some issues with the input data will be noted but will not cause the title to
fail checks.
"""

import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

from validator_lib.validator_config import ValidatorConfig

class IssuesChooser:

    error_glossary_url = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md'

    def __init__(self, issn_db_missing=False):

        self.validator_config = ValidatorConfig()

        self.issn_db_missing = issn_db_missing

        # Issue categories that should be at the top of sections.
        self.break_categories = {
            'binding_words_in_holdings', 'duplicate_holdings_id', 'holdings_out_of_range', 'invalid_local_issn', 
            'oclc_mismatch', 'line_583_error' }

        self.window = None
        self.create_main_window()

    def create_main_window(self):
        """
        The main process.
        """
        self.warnings = []

        self.window = tk.Tk()
        self.window.title('Select disqualifying_issues')
        window_width = 640
        window_height = 640
        self.window.geometry("{}x{}".format(window_width, window_height))

        canvas = tk.Canvas(self.window)
        scroll_y = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)

        title_text = 'Select Disqualifying Issues'

        Font_tuple = ("sans", 12, "bold")

        title_frame = tk.LabelFrame(self.window)
        title_label = tk.Label(self.window, text=title_text, justify=tk.LEFT, wraplength=600, fg="black", bg="white")
        title_label.configure(font=Font_tuple)
        title_label.pack()

        # spacer bar
        tk.Frame(self.window, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        f = tk.Frame(canvas)
        self.int_vars = {}

        issues_frame = tk.Frame(f)

        row_no = 1
        col_no = 0
        for issue in self.validator_config.config['disqualifying_issues']:
            # TODO: This isn't actually breaking the inputs
            if issue in self.break_categories:
                col_no = 0
                row_no += 1
                break_label = tk.Label(issues_frame, text='')
                break_label.grid(row=row_no, column=col_no, sticky=tk.W)
                row_no += 1
            self.int_vars[issue] = tk.IntVar()            
            if 'issn_db' in issue and self.issn_db_missing is True:
                self.int_vars[issue].set(0)
                tk.Checkbutton(issues_frame, text=issue, state=tk.DISABLED, variable=self.int_vars[issue]).grid(row=row_no, column=col_no, sticky=tk.W)
            else:
                self.int_vars[issue].set(self.validator_config.config['disqualifying_issues'][issue])
                tk.Checkbutton(issues_frame, text=issue, variable=self.int_vars[issue]).grid(row=row_no, column=col_no, sticky=tk.W)

            col_no += 1
            if col_no == 2:
                row_no += 1
                col_no = 0
        row_no += 1

        issues_frame.pack(anchor=tk.W, fill=tk.X, padx=5, pady=5)

        btn_frame = tk.Frame(f)
        btn_save = tk.Button(btn_frame, text="Save", command=self.ok_clicked)
        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self.cancelled)
        btn_reset = tk.Button(btn_frame, text="Defaults", command=self.reset_fields)
        btn_save.grid(column=0, row=0)
        btn_cancel.grid(column=1, row=0)
        btn_reset.grid(column=2, row=0)
        btn_frame.pack()

        docs_link_label = tk.Label(self.window, text="Click here to open a web browser to visit a glossary of issue codes in the documentation", fg="blue", cursor="hand2")
        docs_link_label.pack()
        docs_link_label.bind("<Button-1>", lambda e: webbrowser.open(self.error_glossary_url))

        canvas.create_window(0, 0, anchor="nw", window=f)
        canvas.update_idletasks()

        canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)

        canvas.pack(fill='both', expand=True, side='left')
        scroll_y.pack(fill='y', side='right')

        self.window.lift()

        self.window.mainloop()

    def open_glossary_on_wiki(self):
        webbrowser.open(self.error_glossary_url)

    def ok_clicked(self):
        for issue in self.validator_config.config['disqualifying_issues']:
            issue_state = self.int_vars[issue].get()
            self.validator_config.config['disqualifying_issues'][issue] = str(issue_state)
        self.validator_config.write_validator_config_file()
        self.cancelled()

    def cancelled(self):
        """Close without making any changes."""
        self.window.destroy()

    def reset_fields(self):
        self.validator_config.config['disqualifying_issues'] = self.validator_config.get_default_disqualifying_issues()
        self.cancelled()
        self.create_main_window()
