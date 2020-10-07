import utils.colors as c


class Command:
    def __init__(self, players, id):
        self.players = players
        self.id = id
        self.command_codes = [0 for _ in range(len(self.players))]
        self.command_lists = [[] for _ in range(len(self.players))]

    def add(self, command, id=None):
        id = self.id if id is None else id
        cc = self.command_codes[id]
        self.command_codes[id] += 1
        self.command_lists[id].append((command[0], command[1], cc))
        return cc

    def get_own_com_list(self):
        return self.command_lists[self.id]

    def get_cc(self, id=None):
        return self.command_codes[self.id if id is None else id]

    def clear_command(self, id):
        self.command_lists[id] = []

    def clear_commands(self):
        for id in range(len(self.players)):
            self.clear_command(id)

    def trim(self, command_code):
        com_list = self.get_own_com_list()
        while len(com_list) > 0 and com_list[0][2] < command_code:
            com_list.pop(0)

    def show(self, ui, map, *, pan=(0, 0)):
        coms = [set() for _ in range(4)]
        for com in self.get_own_com_list():
            adjacent = map.get_adj_cords(com[0], corner=False, trim=False)
            if com[1] in adjacent:
                coms[adjacent.index(com[1])].add(com[0])
        line_lists = [
            [[(0, -5), (0, -18)], [(-2, -16), (0, -18)], [(2, -16), (0, -18)]],
            [[(-5, 0), (-18, 0)], [(-16, -2), (-18, 0)], [(-16, 2), (-18, 0)]],
            [[(0, 5), (0, 18)], [(-2, 16), (0, 18)], [(2, 16), (0, 18)]],
            [[(5, 0), (18, 0)], [(16, -2), (18, 0)], [(16, 2), (18, 0)]]
        ]
        for i in range(4):
            for com in list(coms[i]):
                pos = (
                    map.pos[0] + com[0] * map.grid_size + map.grid_size // 2 + map.pan[0] + pan[0],
                    map.pos[1] + com[1] * map.grid_size + map.grid_size // 2 + map.pan[1] + pan[1])
                for line in line_lists[i]:
                    ui.show_line(line[0], line[1], color=c.white, pan=pos)
