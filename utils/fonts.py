def get_font(font_name, font_size, font_type='ttf'):
    return 'src', f'{font_name}.{font_type}', font_size


# merriweather light
def tnr(font_size):
    return 'src', 'merriweather.ttf', font_size


# merriweather bold
def tnr_bold(font_size):
    return 'src', 'merriweather-bold.ttf', font_size


# cambria
def cambria(font_size):
    return 'src', 'cambria.ttf', font_size


# digital
def digital_7(font_size):
    return 'src', 'digital-7-mono.ttf', font_size
