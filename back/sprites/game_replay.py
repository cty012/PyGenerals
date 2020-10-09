from datetime import datetime
import json
import socket
from threading import Thread

import back.players.human as h
import back.sprites.modules.command as cm
import back.sprites.modules.map as m
import back.sprites.modules.scoreboard as sb
from utils.parser import Parser


class Game:
    def __init__(self, args, replay):
        self.args = args
        self.replay = replay
        self.name = ''
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.replay['num']]
        self.players = [{'land': 0, 'army': 0, 'color': player_colors[id]} for id in range(self.replay['num'])]
        self.scoreboard = sb.Scoreboard(self.args, (self.args.size[0] - 10, 10), self.players, align=(2, 0))
        self.map = m.Map(
            self.args, self.args.get_pos(1, 1), self.players, 0, map_status=self.replay['init-status'], align=(1, 1))
        self.map.set_status({'visible': [True for _ in range(self.map.dim[0] * self.map.dim[1])]})
        self.command = cm.Command(self.args, self.players, 0)
        self.player = h.Human(self.args, self.map)
        # status
        self.status = {'running': True}

    def process_events(self, events):
        # update map
        if self.map.clock.get_time() >= 0.5:
            # update map
            self.map.turn += 1
            self.map.set_status(self.replay['status'][self.map.turn])
            # update command
            self.command.command_lists = [self.replay['record'][self.map.turn]]
        # process map moves
        map_commands = self.player.process_events(events)
        self.execute(['move-board', map_commands['move-board']])
        self.execute(['move-cursor', map_commands['move-cursor']])
        # pass
        return [None]

    def execute(self, command):
        if command[0] == 'pause':
            self.map.clock.toggle_run()
        elif command[0] == 'move-board':
            self.map.move_board(command[1])
        elif command[0] == 'move-cursor':
            if command[1] != [0, 0]:
                self.map.move_cursor(command[1], None, execute=False)
        return [None]

    def show(self, ui):
        self.map.show(ui)
        self.command.show(ui, self.map)
        self.scoreboard.show(ui)
