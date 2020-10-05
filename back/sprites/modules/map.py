import back.sprites.modules.block as b
import utils.colors as c
import utils.functions as utils


class Map:
    def __init__(self, args, pos, dim=(29, 24), *, align=(0, 0)):
        self.args = args
        self.dim = dim
        # display
        self.grid_size = 40
        self.total_size = self.dim[0] * self.grid_size, self.dim[1] * self.grid_size
        self.pos = utils.top_left(pos, self.total_size, align=align)
        self.pan = (0, 0)
        # blocks
        self.blocks = [[
            b.Block((self.pos[0] + row * self.grid_size, self.pos[1] + col * self.grid_size), self.grid_size, c.gray_0)
            for col in range(self.dim[1])
        ] for row in range(self.dim[0])]

    def move_board(self, direction=(0, 0)):
        step = (-11, -11)
        self.pan = (self.pan[0] + step[0] * direction[0], self.pan[1] + step[1] * direction[1])
        self.pan = (
            utils.min_max(self.pan[0], -self.total_size[0] // 2, self.total_size[0] // 2),
            utils.min_max(self.pan[1], -self.total_size[1] // 2, self.total_size[1] // 2)
        )

    def show_grid(self, ui, *, pan=(0, 0)):
        # vertical lines
        for col in range(self.dim[0] + 1):
            start = (self.pos[0] + col * self.grid_size, self.pos[1])
            end = (self.pos[0] + col * self.grid_size, self.pos[1] + self.dim[1] * self.grid_size)
            ui.show_line(start, end, pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))
        # horizontal lines
        for row in range(self.dim[1] + 1):
            start = (self.pos[0], self.pos[1] + row * self.grid_size)
            end = (self.pos[0] + self.dim[0] * self.grid_size, self.pos[1] + row * self.grid_size)
            ui.show_line(start, end, pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))

    def show(self, ui, *, pan=(0, 0)):
        for row in range(self.dim[0]):
            for col in range(self.dim[1]):
                self.blocks[row][col].show(ui, pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))
        self.show_grid(ui, pan=pan)
