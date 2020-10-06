from itertools import product
from random import choices, randint

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
        self.blocks = None
        self.cities = None
        self.players = players
        self.id = id
        MapLoader.init_blocks(self)

        # update
        self.turn = 1
        self.update_interval = 0.5
        self.city_gen = 2
        self.blank_gen = 50
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
        for row, col in product(range(self.dim[0]), range(self.dim[1])):
            if self.get((row, col)).get_prop(prop) in values:
                blocks.append((row, col))
        return blocks

    def cord_in_range(self, cord):
        return 0 <= cord[0] < self.dim[0] and 0 <= cord[1] < self.dim[1]

    def get_adj_cords(self, cord):
        return [adj_cord for adj_cord in
            [(cord[0], cord[1] - 1), (cord[0] - 1, cord[1]), (cord[0], cord[1] + 1), (cord[0] + 1, cord[1])]
            if self.cord_in_range(adj_cord)
        ]

    def pos_to_cord(self, pos):
        row = int((pos[0] - self.pos[0] - self.pan[0]) // self.grid_size)
        col = int((pos[1] - self.pos[1] - self.pan[1]) // self.grid_size)
        if self.cord_in_range((row, col)):
            return (row, col) if self.get((row, col)).in_range(pos, pan=self.pan) else None
        return None

    def update(self):
        # reset clock
        self.clock.clear()
        self.clock.start()
        self.turn += 1

        # recruit
        if self.turn % self.city_gen == 0:
            for cord in self.cities:
                if self.get(cord).owner is not None:
                    self.get(cord).num += 1
        if self.turn % self.blank_gen == 0:
            for cord in product(range(self.dim[0]), range(self.dim[1])):
                if self.get(cord).owner is not None and self.get(cord).terrain == 'blank':
                    self.get(cord).num += 1

        # execute commands
        for id in range(len(self.players)):
            while len(self.commands[id]) > 0:
                # analyze command
                com = self.commands[id].pop(0)
                block, target = self.get(com[0]), self.get(com[1])
                # skip invalid command
                if block.owner != id:
                    continue
                # execute command
                player_updates = block.move(target)
                # calc effect of command
                for p_update in player_updates:
                    if p_update[0] is not None:
                        self.players[p_update[0]]['num'] += p_update[1]
                break

        # refresh visible
        self.refresh_visible()

    def refresh_visible(self):
        for row, col in product(range(self.dim[0]), range(self.dim[1])):
            self.get((row, col)).visible = False
        for row, col in product(range(self.dim[0]), range(self.dim[1])):
            if self.get((row, col)).owner == self.id:
                self.get((row, col)).visible = True
                for adj_cord in self.get_adj_cords((row, col)):
                    self.get(adj_cord).visible = True

    def move_cursor(self, direction):
        if self.cursor is None:
            return
        target = (self.cursor[0] + direction[0], self.cursor[1] + direction[1])
        if self.cord_in_range(target):
            # record command
            if self.get(self.cursor).owner == self.id or \
                    (len(self.commands[self.id]) > 0 and self.cursor == self.commands[self.id][-1][1]):
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
        # show blocks
        for row, col in product(range(self.dim[0]), range(self.dim[1])):
            self.blocks[row][col].show(
                ui, self.players, is_cursor=(self.cursor == (row, col)),
                pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))
        # show grid
        self.show_grid(ui, pan=pan)
        # show cursor
        if self.cursor is not None:
            ui.show_div(
                (self.pos[0] + self.cursor[0] * self.grid_size, self.pos[1] + self.cursor[1] * self.grid_size),
                (self.grid_size + 1, self.grid_size + 1), border=1, color=c.white,
                pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))


class MapLoader:
    @classmethod
    def init_blocks(cls, map):
        # init blocks
        map.blocks = [[
            b.Block((map.pos[0] + row * map.grid_size, map.pos[1] + col * map.grid_size), map.grid_size)
            for col in range(map.dim[1])] for row in range(map.dim[0])]

        # init cities and bases
        cities_cords = choices(list(product(range(map.dim[0]), range(map.dim[1]))), k=20+len(map.players))
        bases_cords = choices(cities_cords, k=len(map.players))
        for cord in cities_cords:
            map.get(cord).terrain = 'city'
            map.get(cord).num = randint(40, 50)
        for id, cord in enumerate(bases_cords):
            map.get(cord).terrain = 'base'
            map.get(cord).owner = id
            map.get(cord).num = 1

        # init map variables (cities, players, visible)
        map.cities = map.get_blocks_by_prop('terrain', ['base', 'city'])
        for id in range(len(map.players)):
            map.players[id]['num'] = len(map.get_blocks_by_prop('owner', [id]))
        map.refresh_visible()
