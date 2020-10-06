import back.sprites.modules.block as b
import utils.colors as c
import utils.functions as utils
import utils.stopwatch as sw


class Map:
    def __init__(self, args, pos, players, id, dim=(29, 24), *, align=(0, 0)):
        self.args = args
        self.dim = dim

        # display
        self.grid_size = 40
        self.total_size = self.dim[0] * self.grid_size, self.dim[1] * self.grid_size
        self.pos = utils.top_left(pos, self.total_size, align=align)
        self.pan = (0, 0)

        # blocks
        self.cursor = None
        self.blocks = [[
            b.Block((self.pos[0] + row * self.grid_size, self.pos[1] + col * self.grid_size), self.grid_size, c.gray_0)
            for col in range(self.dim[1])
        ] for row in range(self.dim[0])]
        self.cities = self.get_blocks_by_prop('terrain', ['base', 'city'])
        self.players = players
        self.id = id
        for id in range(len(players)):
            self.players[id]['num'] = self.get_blocks_by_prop('owner', [id])

        # update
        self.update_interval = 0.5
        self.clock = sw.Stopwatch()
        self.clock.start()
        self.commands = [[] for _ in range(len(self.players))]

    def process_events(self, events):
        if self.clock.get_time() >= 0.5:
            self.update()
        if events['mouse-left'] == 'down':
            self.cursor = self.pos_to_cord(events['mouse-pos'])
        if 'up' in events['key-down']:
            self.move_cursor((0, -1))
        if 'left' in events['key-down']:
            self.move_cursor((-1, 0))
        if 'down' in events['key-down']:
            self.move_cursor((0, 1))
        if 'right' in events['key-down']:
            self.move_cursor((1, 0))
        return [None]

    def get(self, cord):
        return self.blocks[cord[0]][cord[1]]

    def get_blocks_by_prop(self, prop, values):
        blocks = []
        for row in range(self.dim[0]):
            for col in range(self.dim[1]):
                if self.get((row, col)).get_prop(prop) in values:
                    blocks.append((row, col))
        return blocks

    def pos_to_cord(self, pos):
        row = int((pos[0] - self.pos[0] - self.pan[0]) // self.grid_size)
        col = int((pos[1] - self.pos[1] - self.pan[1]) // self.grid_size)
        if 0 <= row < self.dim[0] and 0 <= col < self.dim[1]:
            return (row, col) if self.get((row, col)).in_range(pos, pan=self.pan) else None
        return None

    def update(self):
        # reset clock
        self.clock.clear()
        self.clock.start()
        # recruit
        for cord in self.cities:
            self.get(cord).num += 1
        # execute commands
        for command in self.commands:
            if len(command) == 0:
                continue
            player_updates = self.get(command[0]).move(self.get(command[1]))
            for p_update in player_updates:
                if p_update[0] is not None:
                    self.players[p_update[0]]['num'] += p_update[1]

    def move_cursor(self, direction):
        if self.cursor is None:
            return
        target = (self.cursor[0] + direction[0], self.cursor[1] + direction[1])
        if 0 <= target[0] < self.dim[0] and 0 <= target[1] < self.dim[1]:
            # record command
            if self.get(self.cursor).owner == self.id:
                if self.get(self.cursor).terrain != 'mountain' and self.get(target).terrain != 'mountain':
                    self.commands[self.id].append((self.cursor, target))
            # move cursor
            self.cursor = target

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
                self.blocks[row][col].show(
                    ui, self.players, is_cursor=(self.cursor == (row, col)),
                    pan=(self.pan[0] + pan[0], self.pan[1] + pan[1])
                )
        self.show_grid(ui, pan=pan)
