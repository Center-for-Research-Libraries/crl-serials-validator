from termcolor import cprint


def print_terminal_page_header(header_str, header_color='green'):
    header_bar = ''.join(['~' for _ in header_str])
    cprint(header_bar, header_color)
    cprint(header_str, header_color)
    cprint(header_bar, header_color)
    print('')
    