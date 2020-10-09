from itertools import product
from random import choices, randint

import back.sprites.modules.block as b
import utils.colors as c
import utils.functions as utils
import utils.stopwatch as sw


class Map:
    def __init__(self, args, pos, players, id, dim=(29, 24), *, map_status=None, align=(0, 0)):
        self.args = args
        self.id = id
        self.dim = dim
        self.prd = tuple(product(range(self.dim[0]), range(self.dim[1])))
        self.eprd = tuple(enumerate(self.prd))

        # display
        self.grid_size = 40
        self.total_size = self.dim[0] * self.grid_size, self.dim[1] * self.grid_size
        self.pos = utils.top_left(pos, self.total_size, align=align)
        self.pan = (0, 0)

        # cursor and blocks
        self.cursor = None
        self.blocks = None
        self.cities = None
        self.players = players
        self.init_status = None
        MapLoader.init_blocks(self, map_status=map_status)

        # update
        self.turn = 0
        self.update_interval = 0.5
        self.city_gen = 2
        self.blank_gen = 50
        self.clock = sw.Stopwatch()
        self.clock.start()

        # record
        self.record = [[None for _ in self.players]]

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

    def get_alive(self):
        alive = []
        for id in range(len(self.players)):
            if self.get_base(id) is not None:
                alive.append(id)
        return alive

    def get_winner(self):
        alive = self.get_alive()
        return alive[0] if len(alive) == 1 else None

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
        new_record = [None for _ in range(len(self.players))]
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
                new_record[id] = [com[0], com[1]]
                # calc effect of command
                for p_update in player_updates:
                    if p_update[0] == 'conquer':
                        self.conquer(p_update[1], p_update[2])
                        yield ['conquer', p_update[1], p_update[2]]
                break
        self.record.append(new_record)

        # refresh
        self.refresh()
        return [None]

    def refresh(self, items=('visible', 'player')):
        # refresh visible, player num
        # reset
        if 'player' in items:
            for player in self.players:
                player['land'] = 0
                player['army'] = 0
        if 'visible' in items:
            for row, col in self.prd:
                self.get((row, col)).visible = False

        # check
        for row, col in self.prd:
            block = self.get((row, col))
            if 'player' in items:
                if block.owner is not None:
                    self.players[block.owner]['land'] += 1
                    self.players[block.owner]['army'] += block.num
            if 'visible' in items:
                if block.owner == self.id:
                    self.get((row, col)).visible = True
                    for adj_cord in self.get_adj_cords((row, col)):
                        self.get(adj_cord).visible = True

    def move_cursor(self, direction, command, execute=True):
        if self.cursor is None:
            return

        target = (self.cursor[0] + direction[0], self.cursor[1] + direction[1])

        if not execute:
            if self.cord_in_range(target):
                self.cursor = target
            return

        command_list = command.get_own_com_list()

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

    def move_board(self, direction=(0, 0)):
        step = (-11, -11)
        self.pan = (self.pan[0] + step[0] * direction[0], self.pan[1] + step[1] * direction[1])
        self.pan = (
            utils.min_max(self.pan[0], -self.total_size[0] // 2, self.total_size[0] // 2),
            utils.min_max(self.pan[1], -self.total_size[1] // 2, self.total_size[1] // 2)
        )

    def conquer(self, p1, p2):
        for cord in self.prd:
            block = self.get(cord)
            if block.owner == p2:
                block.owner = p1
                if block.terrain == 'base':
                    block.terrain = 'city'

    def get_status(self, fields=('owner', 'num')):
        return {
            field: [self.get(cord).get_prop(field) for cord in self.prd]
            for field in fields
        }

    def set_status(self, status, refresh=True):
        for field in status.keys():
            for i, cord in self.eprd:
                self.get(cord).set_prop(field, status[field][i])
        if refresh:
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
        map_status = cls.generate_map_status(map.dim, len(map.players)) if map_status is None else map_status
        map.init_status = map_status

        # init blocks from info in map_status
        map.blocks = [[
            b.Block(
                (map.pos[0] + row * map.grid_size, map.pos[1] + col * map.grid_size), map.grid_size,
                owner=map_status[row][col]['owner'], num=map_status[row][col]['num'], terrain=map_status[row][col]['terrain'])
            for col in range(map.dim[1])] for row in range(map.dim[0])]

        # init map variables (cities, players, visible)
        map.cities = map.get_blocks_by_prop('terrain', ['base', 'city'])
        for id in range(len(map.players)):
            map.players[id]['land'] = map.players[id]['army'] = len(map.get_blocks_by_prop('owner', [id]))
        base = map.get_base(map.id)
        map.pan = (
            map.total_size[0] // 2 - base[0] * map.grid_size - map.grid_size // 2,
            map.total_size[1] // 2 - base[1] * map.grid_size - map.grid_size // 2)

    @classmethod
    def generate_map_status(cls, dim, num_players):
        # create empty blocks
        map_status = [[{'terrain': 'blank', 'owner': None, 'num': 0}
            for col in range(dim[1])] for row in range(dim[0])]

        # create cities and bases
        special_cords = choices(list(product(range(dim[0]), range(dim[1]))), k=100 + num_players)
        mountain_cords, city_cords, base_cords = special_cords[:80], special_cords[80:100], special_cords[100:]
        for x, y in mountain_cords:
            map_status[x][y]['terrain'] = 'mountain'
        for x, y in city_cords:
            map_status[x][y]['terrain'] = 'city'
            map_status[x][y]['num'] = randint(40, 50)
        for id, (x, y) in enumerate(base_cords):
            map_status[x][y]['terrain'] = 'base'
            map_status[x][y]['owner'] = id
            map_status[x][y]['num'] = 1

        return map_status
