import utils.functions as utils


rgb = lambda *a: a

white = rgb(255, 255, 255)
black = rgb(0, 0, 0)
dark_gray = rgb(64, 64, 64)
gray_0 = rgb(224, 224, 224)
gray_1 = rgb(192, 192, 192)
gray_2 = rgb(128, 128, 128)

p_red = rgb(255, 0, 0)
p_blue = rgb(0, 0, 255)
p_green = rgb(0, 128, 0)
p_yellow = rgb(200, 150, 0)
p_cyan = rgb(0, 160, 160)
p_magenta = rgb(180, 35, 260)
p_brown = rgb(128, 80, 0)
p_lavender = rgb(190, 160, 220)

get_player_colors = lambda: [p_red, p_blue, p_green, p_yellow, p_cyan, p_magenta, p_brown, p_lavender]


def add(color, num):
    return tuple((utils.min_max(color[i] + num, 0, 255)) for i in (0, 1, 2))
