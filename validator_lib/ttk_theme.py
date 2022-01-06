from tkinter import ttk
from ttkbootstrap import Style
import ttkbootstrap



def set_ttk_style(tk_object=None):
    """
    Set the default ttk style in one place.
    """
    # style = ttk.Style()
    style = ttkbootstrap.Style(theme='flatly')
    return style
