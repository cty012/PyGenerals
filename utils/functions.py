# return the top-left corner of the rectangle
def top_left(pos, size, *, align=(0, 0)):
    return pos[0] - align[0] * (size[0] // 2), pos[1] - align[1] * (size[1] // 2)


# whether two rectangles overlap
def overlap(rect1, rect2):
    return is_rect([rect1[0], rect2[1]]) and is_rect([rect2[0], rect1[1]])


def direction(rect1, rect2, direct):
    if max(rect1[0][direct], rect1[1][direct]) <= min(rect2[0][direct], rect2[1][direct]):
        return 'low'
    elif min(rect1[0][direct], rect1[1][direct]) >= max(rect2[0][direct], rect2[1][direct]):
        return 'high'
    return None


def is_rect(rect):
    return rect[0][0] < rect[1][0] and rect[0][1] < rect[1][1]


def is_private_ip(ip):
    return ip.startswith('10.') or ip.startswith('172.') or ip.startswith('192.')
