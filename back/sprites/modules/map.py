from itertools import product
from random import choices, randint

import back.sprites.modules.block as b
import utils.colors as c
import utils.functions as utils
import utils.stopwatch as sw


class Map:
    def __init__(self, args, pos, players, id, dim=(29, 24), *, map_status=None, align=(0, 0)):
        self.args = args
        self.dim = dim
        self.prd = tuple(product(range(self.dim[0]), range(self.dim[1])))
        self.eprd = tuple(enumerate(self.prd))

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
        MapLoader.init_blocks(self, map_status=map_status)

        # update
        self.turn = 1
        self.update_interval = 0.5
        self.city_gen = 2
        self.blank_gen = 50
        self.clock = sw.Stopwatch()
        self.clock.start()

        # refresh
        self.refresh()

    def get(self, cord):
        return self.blocks[cord[0]][cord[1]]

    def get_blocks_by_prop(self, prop, values):
        blocks = []
        for row, col in self.prd:
            if self.get((row, col)).get_prop(prop) in values:
                blocks.append((row, col))
        return blocks

    def get_base(self, id):
        for row, col in self.prd:
            if self.get((row, col)).owner == id and self.get((row, col)).terrain == 'base':
                return row, col

    def cord_in_range(self, cord):
        return 0 <= cord[0] < self.dim[0] and 0 <= cord[1] < self.dim[1]

    def get_adj_cords(self, cord, corner=True, trim=True):
        return [adj_cord for adj_cord in
            [(cord[0], cord[1] - 1), (cord[0] - 1, cord[1]), (cord[0], cord[1] + 1), (cord[0] + 1, cord[1])] +
            ([(cord[0] - 1, cord[1] - 1), (cord[0] - 1, cord[1] + 1), (cord[0] + 1, cord[1] - 1), (cord[0] + 1, cord[1] + 1)]
            if corner else [])
            if not trim or self.cord_in_range(adj_cord)
        ]

    def pos_to_cord(self, pos):
        row = int((pos[0] - self.pos[0] - self.pan[0]) // self.grid_size)
        col = int((pos[1] - self.pos[1] - self.pan[1]) // self.grid_size)
        if self.cord_in_range((row, col)):
            return (row, col) if self.get((row, col)).in_range(pos, pan=self.pan) else None
        return None

    def update(self, command):
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
            for cord in self.prd:
                if self.get(cord).owner is not None and self.get(cord).terrain == 'blank':
                    self.get(cord).num += 1

        # execute commands
        for id in range(len(self.players)):
            com_list = command.command_lists[id]
            while len(com_list) > 0:
                # analyze command
                com = com_list.pop(0)
                block, target = self.get(com[0]), self.get(com[1])
                # skip invalid command
                if block.owner != id or block.num <= 1:
                    continue
                # execute command
                player_updates = block.move(target)
                # calc effect of command
                for p_update in player_updates:
                    if p_update[0] == 'conquer':
                        self.conquer(p_update[1], p_update[2])
                        return ['conquer', p_update[1], p_update[2]]
                break

        # refresh
        self.refresh()

    def refresh(self):
        # refresh visible, player num, and commands
        # reset
        for player in self.players:
            player['land'] = 0
            player['army'] = 0
        for row, col in self.prd:
            self.get((row, col)).visible = False

        # check
        for row, col in self.prd:
            block = self.get((row, col))
            if block.owner is not None:
                self.players[block.owner]['land'] += 1
                self.players[block.owner]['army'] += block.num
            if block.owner == self.id:
                self.get((row, col)).visible = True
                for adj_cord in self.get_adj_cords((row, col)):
                    self.get(adj_cord).visible = True

    def move_cursor(self, direction, command):
        if self.cursor is None:
            return

        command_list = command.get_own_com_list()
        target = (self.cursor[0] + direction[0], self.cursor[1] + direction[1])

        def controllable(cord, id):
            return self.get(cord).owner == id or (len(command_list) > 0 and cord == command_list[-1][1])

        def not_mountain(cord):
            return self.get(cord).terrain != 'mountain'

        # valid target & cursor's block is controllable & not mountain
        if self.cord_in_range(target):
            if controllable(self.cursor, self.id) and not_mountain(target):
                # record command
                com_code = command.add((self.cursor, target), self.id)
                # move cursor
                orig_cursor = self.cursor
                self.cursor = target
                return [orig_cursor, target, com_code]
            self.cursor = target

    def conquer(self, p1, p2):
        for cord in self.prd:
            block = self.get(cord)
            if block.owner == p2:
                block.owner = p1
                if block.terrain == 'base':
                    block.terrain = 'city'

    def move_board(self, direction=(0, 0)):
        step = (-11, -11)
        self.pan = (self.pan[0] + step[0] * direction[0], self.pan[1] + step[1] * direction[1])
        self.pan = (
            utils.min_max(self.pan[0], -self.total_size[0] // 2, self.total_size[0] // 2),
            utils.min_max(self.pan[1], -self.total_size[1] // 2, self.total_size[1] // 2)
        )

    def get_status(self, fields=('owner', 'num')):
        return {
            field: [self.get(cord).get_prop(field) for cord in self.prd]
            for field in fields
        }

    def set_status(self, status):
        for field in status.keys():
            for i, cord in self.eprd:
                self.get(cord).set_prop(field, status[field][i])
        self.refresh()

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
        for row, col in self.prd:
            self.blocks[row][col].show(ui, self.players, pan=(self.pan[0] + pan[0], self.pan[1] + pan[1]))
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
    def init_blocks(cls, map, *, map_status):
        if map_status is None:
            # init blocks
            map.blocks = [[
                b.Block((map.pos[0] + row * map.grid_size, map.pos[1] + col * map.grid_size), map.grid_size)
                for col in range(map.dim[1])] for row in range(map.dim[0])]

            # init cities and bases
            special_cords = choices(map.prd, k=100+len(map.players))
            mountain_cords, city_cords, base_cords = special_cords[:80], special_cords[80:100], special_cords[100:]
            for cord in mountain_cords:
                map.get(cord).terrain = 'mountain'
            for cord in city_cords:
                map.get(cord).terrain = 'city'
                map.get(cord).num = randint(40, 50)
            for id, cord in enumerate(base_cords):
                map.get(cord).terrain = 'base'
                map.get(cord).owner = id
                map.get(cord).num = 1

        else:
            # init blocks
            map.blocks = [[None for col in range(map.dim[1])] for row in range(map.dim[0])]
            for i, (row, col) in map.eprd:
                map.blocks[row][col] = b.Block(
                    (map.pos[0] + row * map.grid_size, map.pos[1] + col * map.grid_size), map.grid_size,
                    owner=map_status['owner'][i], num=map_status['num'][i], terrain=map_status['terrain'][i])

        # init map variables (cities, players, visible)
        map.cities = map.get_blocks_by_prop('terrain', ['base', 'city'])
        for id in range(len(map.players)):
            map.players[id]['land'] = map.players[id]['army'] = len(map.get_blocks_by_prop('owner', [id]))
        base = map.get_base(map.id)
        map.pan = (
            map.total_size[0] // 2 - base[0] * map.grid_size - map.grid_size // 2,
            map.total_size[1] // 2 - base[1] * map.grid_size - map.grid_size // 2)
