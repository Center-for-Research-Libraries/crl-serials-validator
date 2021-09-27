import tkinter as tk
import tkinter.ttk as ttk

from validator_lib.ttk_theme import set_ttk_style
from crl_lib.api_keys import OclcApiKeys


class ApiKeySetter(tk.Tk):
    """
    Very simple Tkinter class to allow the user to more easily set API keys.

    Usage:

        a = ApiKeySetter()

    Then copy and paste your keys. That's it!

    The script will print a copy of your names/keys to the console, if it is
    run from a command line.
    """
    def __init__(self, data_folder):
        """
        data_folder should be the location (or desired location) of the API keys config file.

        style is an optional ttk style.
        """
        super().__init__()
        self.api_keys = OclcApiKeys(data_folder)
        self.names = list(self.api_keys.api_keys.keys())

        # in case the window pops under the terminal
        print("Opening separate API key setter window.")

        self.title("Set WorldCat Search API keys")

        style = set_ttk_style(self)

        # lbl = ttk.Label(self, text="Set WorldCat Search API keys", font=("Arial Bold", 14))
        # lbl.grid(column=1, row=0)

        label_name = ttk.Label(self, text="Name")
        label_key = ttk.Label(self, text="API Key")
        label_name.grid(column=0, row=1)
        label_key.grid(column=1, row=1)

        self.selected = tk.IntVar()

        self.inputs = []
        for i in range(0, 6):
            is_default = False
            try:
                name = self.names[i]
                api_key = self.api_keys.api_keys[name]
                if self.api_keys.api_key_name == name:
                    is_default = True
            except IndexError:
                name = ""
                api_key = ""
            self.inputs.append({
                "name": ttk.Entry(self, width=10),
                "key": ttk.Entry(self, width=100),
                "radio": ttk.Radiobutton(text='Default', value=i, variable=self.selected)
            })
            self.inputs[i]["name"].insert(0, name)
            self.inputs[i]["key"].insert(0, api_key)
            if is_default:
                self.inputs[i]["radio"].invoke()

            self.inputs[i]["name"].grid(column=0, row=i+2)
            self.inputs[i]["key"].grid(column=1, row=i+2)
            self.inputs[i]["radio"].grid(column=2, row=i+2)

        btn_frame = ttk.Frame()
        btn_save = ttk.Button(btn_frame, text="Save", command=self.clicked, style='success.TButton')
        spacer = ttk.Label(btn_frame)
        btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.cancelled, style='warning.TButton')
        btn_save.grid(column=0, row=0)
        spacer.grid(column=1, row=0)
        btn_cancel.grid(column=2, row=0)
        btn_frame.grid(row=9, column=2)

        # put the window more towards the center of the screen
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 4)
        y = (hs / 4)
        self.geometry('+%d+%d' % (x, y))
        self.lift()

        self.mainloop()

    def clicked(self):
        """Save clicked. Look for API keys and default key set and save to config file."""
        new_api_keys = {}
        default_key = self.selected.get()
        default_key_name = None
        for i in range(0, 6):
            name = self.inputs[i]["name"].get()
            api_key = self.inputs[i]["key"].get()
            if name and api_key:
                new_api_keys[name] = api_key
                if i == default_key:
                    default_key_name = name
        if new_api_keys:
            self.api_keys.config['API KEYS'] = {}
            for name in new_api_keys:
                self.api_keys.config['API KEYS'][name] = new_api_keys[name]
        if default_key_name:
            self.api_keys.config['Preferred API Key'] = {default_key_name: 1}

        self.api_keys.write_preferences_to_file()
        self.destroy()

    def cancelled(self):
        """Cancel pressed. Close the window."""
        self.destroy()


if __name__ == "__main__":
    a = ApiKeySetter('')
