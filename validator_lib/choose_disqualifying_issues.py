"""
Class to allow the user to decide that some issues with the input data will be noted but will not cause the title to
fail checks.
"""

import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

from validator_lib.validator_config import ValidatorConfig
from validator_lib.ttk_theme import set_ttk_style

class IssuesChooser(tk.Tk):

    error_glossary_url = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md'

    # Issue categories that should be at the top of sections.
    break_categories = {
        'binding_words_in_holdings', 'duplicate_holdings_id', 'holdings_out_of_range', 'title_in_jstor', 
        'invalid_local_issn', 'oclc_mismatch', 'line_583_error' }

    window_width = 640
    window_height = 640

    title_text = 'Select Disqualifying Issues'

    def __init__(self, issn_db_missing=False):
        super().__init__()

        self.issn_db_missing = issn_db_missing
        self.validator_config = ValidatorConfig()

        self.warnings = []
        self.int_vars = {}

        # style = ttk.Style()
        # style.theme_use('clam')

        # style.configure('TFrame', background='yellow')

        # style.configure('link.TButton', foreground='blue')

        # style.configure('save.TButton')
        # style.map('save.TButton', background=[('active', 'lightgreen')])

        # style.configure('cancel.TButton')
        # style.map('cancel.TButton', background=[('active', '#FF7F7F')])

        # style.configure('defaults.TButton')
        # style.map('defaults.TButton', background=[('active', 'lightblue')])

        style = set_ttk_style(self)

        start_x, start_y = self.get_center_location()
        # self.geometry('{}x{}+{}+{}'.format(self.window_width, self.window_height, start_x, start_y))
        self.resizable(1, 1)
        self.title('Select disqualifying_issues')
        
        # canvas = tk.Canvas(self)
        # scroll_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)

        # title_frame = ttk.LabelFrame(self)
        # title_label = ttk.Label(self, text=self.title_text, justify=tk.LEFT, wraplength=600)
        # title_label.pack()
        
        spacer_top = tk.Label(text='')
        spacer_top.pack()
        docs_link_label = ttk.Button(self, text="Click here to visit a glossary of issue codes in a web browser")
        docs_link_label['style'] = 'info.TButton'
        docs_link_label.pack(fill='x')
        docs_link_label.bind("<Button-1>", lambda e: webbrowser.open(self.error_glossary_url))

        issues_frame = ttk.Frame()

        row_no = 1
        col_no = 0
        for issue in self.validator_config.config['disqualifying_issues']:
            if issue in self.break_categories:
                col_no = 0
                row_no += 1
                break_label = ttk.Label(issues_frame, text='')
                break_label.grid(row=row_no, column=col_no, sticky=tk.W)
                row_no += 1
            self.int_vars[issue] = tk.IntVar()    

            if 'issn_db' in issue and self.issn_db_missing is True:
                self.int_vars[issue].set(0)
                ttk.Checkbutton(issues_frame, text=issue, state=tk.DISABLED, variable=self.int_vars[issue]).grid(row=row_no, column=col_no, sticky=tk.W, ipady=2)
            else:
                self.int_vars[issue].set(self.validator_config.config['disqualifying_issues'][issue])
                ttk.Checkbutton(issues_frame, text=issue, variable=self.int_vars[issue]).grid(row=row_no, column=col_no, sticky=tk.W, ipady=2)

            col_no += 1
            if col_no == 2:
                row_no += 1
                col_no = 0
        row_no += 1

        issues_frame.pack(anchor=tk.W, fill=tk.X, padx=5, pady=5)

        btn_frame = ttk.Frame(padding='10')
        btn_save = ttk.Button(btn_frame, text="Save", style="success.TButton", command=self.ok_clicked)
        btn_cancel = ttk.Button(btn_frame, text="Cancel", style="warning.TButton",  command=self.cancelled)
        btn_reset = ttk.Button(btn_frame, text="Defaults", style="danger.TButton",  command=self.reset_fields)
        btn_save.grid(column=0, row=0)
        spacer1 = tk.Label(btn_frame)
        spacer1.grid(column=1, row=0)
        btn_cancel.grid(column=2, row=0)
        spacer2 = tk.Label(btn_frame)
        spacer2.grid(column=3, row=0)
        btn_reset.grid(column=4, row=0)
        btn_frame.pack()

        # canvas.create_window(0, 0, anchor="nw")
        # canvas.update_idletasks()

        # canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)

        # canvas.pack(fill='both', expand=True, side='left')
        # scroll_y.pack(fill='y', side='right')

        self.mainloop()

    def get_center_location(self):
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        start_x = int((width / 2) - (self.window_width / 2))
        start_y = int((height / 2) - (self.window_height / 2))
        return start_x, start_y

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
        self.destroy()

    def reset_fields(self):
        self.validator_config.config['disqualifying_issues'] = self.validator_config.get_default_disqualifying_issues()
        self.validator_config.write_validator_config_file()
        self.cancelled()
        self.__init__(self.issn_db_missing)


if __name__ == "__main__":
    IssuesChooser()
