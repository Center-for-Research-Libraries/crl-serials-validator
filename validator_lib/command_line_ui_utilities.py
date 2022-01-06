from termcolor import cprint, colored
from random import choice


def print_breaking_bar(
    breaking_character='-', bar_length=30, breaking_color='yellow', highlight_color=None, breaking_text=None):
    breaking_bar = ''
    if breaking_text:
        bar_length = len(str(breaking_text))
    while bar_length > 0:
        breaking_bar += breaking_character
        bar_length -= 1
    if highlight_color and not highlight_color.startswith('on_'):
        background_color = 'on_' + highlight_color
    cprint(breaking_bar, breaking_color, highlight_color)


def get_random_color(previous_color=None, colors_to_skip=()):
    colors = ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    color = get_random_attribute(colors, previous_color, colors_to_skip)
    return color


def get_random_highlight_color(main_color=None, previous_highlight=None, highlights_to_skip = ()):
    if not main_color:
        main_color = 'white'
    highlights = ['on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta', 'on_cyan', 'on_white']
    attempts = 0
    while attempts < 5:
        attempts += 1
        highlight = get_random_attribute(highlights, previous_highlight, highlights_to_skip)
        if not main_color or main_color not in highlight:
            return highlight
    return None


def get_random_attribute(previous_attribute=None, attributes_to_skip=()):
    attributes = ['bold', 'dark', 'underline', 'blink', 'reverse', 'concealed']
    attribute = get_random_element(attributes, previous_attribute, attributes_to_skip)
    return attribute


def get_random_element(element_list, previous_element, elements_to_skip):
    """
    Get a random color, highlight, or attribute.
    """
    if previous_element:
        try:
            element_list.remove(previous_element)
        except ValueError:
            pass
    for element_to_skip in elements_to_skip:
        try:
            element_list.remove(element_to_skip)
        except ValueError:
            pass
    if element_list:
        return choice(element_list)
    return None
