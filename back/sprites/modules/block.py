import utils.functions as utils


class Block:
    def __init__(self, pos, size, color, terrain='blank', *, align=(0, 0)):
        self.size = size
        self.pos = utils.top_left(pos, (self.size, self.size), align=align)
        # contents
        self.color = color
        self.terrain = terrain  # blank, base, city, mountain

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(self.pos, (self.size, self.size), color=self.color, pan=pan)
