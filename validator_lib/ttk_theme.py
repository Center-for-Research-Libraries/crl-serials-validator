from ttkbootstrap import Style


def set_ttk_style(tk_object=None):
    """
    Set the default ttk style in one place.
    """
    style = Style(theme='yeti')

    return style