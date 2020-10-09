import utils.functions as utils


white = (255, 255, 255)
black = (0, 0, 0)
dark_gray = (64, 64, 64)
gray_0 = (224, 224, 224)
gray_1 = (192, 192, 192)
gray_2 = (128, 128, 128)


def add(color, num):
    return tuple((utils.min_max(color[i] + num, 0, 255)) for i in (0, 1, 2))
