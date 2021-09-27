from tkinter import ttk
import tkinter as tk
import platform

def set_theme(tk_object=None):
    """
    This will be used to set a default ttk style, once we come up with one.
    """

    bg_color = '#fafafa'
    fg_color = '#202020'
    disabled_fg_color = "#a0a0a0"
    selected_fg_color = "#ffffff"
    selected_bg_color = "#2f60d8"

    # if tk_object:
    #     tk_object.configure(bg=bg_color)

    style = ttk.Style()

    if platform.system() == 'Windows':
        style.theme_use('winnative')
    elif platform.system() == 'Darwin':
        style.theme_use('aqua')
    else:
        style.theme_use('clam')

    # style.configure('TFrame', background=bg_color, foreground=fg_color)
    # style.configure('TLabel', background=bg_color, foreground=fg_color)
    # style.configure('TCheckbutton', background=bg_color, foreground=fg_color, selected=selected_fg_color)

    style.configure('link.TButton', foreground='darkblue')

    style.configure('save.TButton')
    # style.map('save.TButton', background=[('active', 'lightgreen')])

    style.configure('cancel.TButton')
    # style.map('cancel.TButton', background=[('active', '#FF7F7F')])

    style.configure('defaults.TButton')
    # style.map('defaults.TButton', background=[('active', 'lightblue')])

    return style