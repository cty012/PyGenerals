import json
import socket
from threading import Thread
import time

import back.players.human as h
import back.sprites.modules.command as cm
import back.sprites.modules.map as m
import back.sprites.modules.scoreboard as sb
from utils.parser import Parser


class Game:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.mode['num']]
        self.players = [{'land': 0, 'army': 0, 'color': player_colors[id]} for id in range(self.mode['num'])]
        self.scoreboard = sb.Scoreboard(self.args, (self.args.size[0] - 10, 10), self.players, align=(2, 0))
        self.command = cm.Command(self.args, self.players, self.mode['id'])
        self.map_status = None
        # connect
        self.status = {'connected': True}
        self.thread_recv = Thread(target=self.receive, name='recv', daemon=True)
        self.thread_recv.start()
        # map
        while self.map_status is None:
            time.sleep(0.01)
        self.map = m.Map(self.args, self.args.get_pos(1, 1), self.players, self.mode['id'], map_status=self.map_status, align=(1, 1))
        self.player = h.Human(self.args, self.map)

    def process_events(self, events):
        # process map
        map_commands = self.player.process_events(events)
        if map_commands['clear']:
            self.command.clear_command(self.mode['id'])
            self.send(json.dumps({'tag': 'clear'}))
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
                move = self.map.move_cursor(command[1], self.command)
                if move is not None:
                    self.send(json.dumps({'tag': 'move', 'move': move}))
        return [None]

    def send(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            self.mode['socket'].send(msg_b_len_b)
            self.mode['socket'].send(msg_b)
        except OSError as e:
            print(e)

    def receive(self):
        parser = Parser()
        print(f'CLIENT START receiving FROM SERVER...')
        while self.status['connected']:
            # receive and parse msg
            try:
                msg_strs = parser.parse(self.mode['socket'].recv(1 << 20))
            except socket.timeout:
                continue
            except json.decoder.JSONDecodeError:
                print('\tJSON Decode Error!')
                continue
            # deal with msg
            for msg_str in msg_strs:
                msg = json.loads(msg_str)
                if msg['tag'] == 'status':
                    self.map.turn = msg['turn']
                    self.command.trim(msg['cc'])
                    self.map.set_status(msg['status'])
                elif msg['tag'] == 'init':
                    self.map_status = msg['status']
                elif msg['tag'] == 'conquer':
                    self.map.conquer(msg['players'][0], msg['players'][1])
        print(f'CLIENT END receiving FROM SERVER...')

    def show(self, ui):
        self.map.show(ui)
        self.command.show(ui, self.map)
        self.scoreboard.show(ui)
