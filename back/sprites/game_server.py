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
    def __init__(self, args, mode, init_status=None):
        self.args = args
        self.date = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = self.date
        self.mode = mode
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.mode['num']]
        self.players = [{'land': 0, 'army': 0, 'color': player_colors[id]} for id in range(self.mode['num'])]
        self.scoreboard = sb.Scoreboard(self.args, (self.args.size[0] - 10, 10), self.players, align=(2, 0))
        self.map = m.Map(
            self.args, self.args.get_pos(1, 1), self.players, self.mode['id'], map_status=init_status, align=(1, 1))
        self.command = cm.Command(self.args, self.players, self.mode['id'])
        self.player = h.Human(self.args, self.map)
        # record
        self.status_record = []
        # connect
        self.status = {
            'connected': [False if id == 0 else True for id in range(self.mode['num'])], 'running': True, 'winner': None}
        self.thread_recv = []
        for id in range(1, self.mode['num']):
            new_thread = Thread(target=self.receive(id), name=f'recv-{id}', daemon=True)
            new_thread.start()
            self.thread_recv.append(new_thread)
        self.sends(json.dumps({'tag': 'init', 'status': self.map.init_status}))

    def process_events(self, events):
        # update map
        if self.map.clock.get_time() >= 0.5:
            # update map
            for command in self.map.update(self.command):
                self.execute(command)
            # record status
            status = self.map.get_status(('owner', 'num', 'terrain'))
            self.status_record.append(status)
            # send status
            for id in range(1, self.mode['num']):
                self.send(json.dumps({
                    'tag': 'status', 'turn': self.map.turn, 'cc': self.command.get_lowest_cc(id),
                    'status': {field: status[field] for field in ('owner', 'num')}}), id)
        # process map moves
        map_commands = self.player.process_events(events)
        if map_commands['clear']:
            self.command.clear_command(self.mode['id'])
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
                self.map.move_cursor(command[1], self.command)
        elif command[0] == 'conquer':
            self.sends(json.dumps({'tag': 'conquer', 'players': [command[1], command[2]]}))
            self.status['winner'] = self.map.get_winner()
        elif command[0] == 'close':
            if self.mode['num'] > 1:
                for id in range(1, self.mode['num']):
                    if self.status['connected'][id]:
                        self.send(json.dumps({'tag': 'close'}), id)
                        self.status['connected'][id] = False
            self.close()
        return [None]

    def send(self, msg, id):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            client = self.mode['clients'][id - 1]
            client['socket'].send(msg_b_len_b)
            client['socket'].send(msg_b)
        except OSError as e:
            print(e)

    def sends(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            for client in self.mode['clients']:
                client['socket'].send(msg_b_len_b)
                client['socket'].send(msg_b)
        except OSError as e:
            print(e)

    def receive(self, id):
        def func():
            parser = Parser()
            client = self.mode['clients'][id-1]
            print(f'SERVER START receiving FROM CLIENT-{id}...')
            while self.status['connected'][id]:
                # receive and parse msg
                try:
                    msg_strs = parser.parse(client['socket'].recv(1 << 20))
                except socket.timeout:
                    continue
                except json.decoder.JSONDecodeError:
                    print('\tJSON Decode Error!')
                    continue
                # deal with msg
                for msg_str in msg_strs:
                    msg = json.loads(msg_str)
                    if msg['tag'] == 'close':
                        self.status['connected'][id] = False
                    if msg['tag'] == 'move':
                        self.command.add((tuple(msg['move'][0]), tuple(msg['move'][1]), msg['move'][2]), id)
                    elif msg['tag'] == 'clear':
                        self.command.clear_command(id)
            print(f'SERVER END receiving FROM CLIENT-{id}...')
        return func

    def close(self):
        self.mode['socket'].close()
        self.status['running'] = False

    def get_json(self):
        return {
            'date': self.date,
            'num': self.mode['num'],
            'turn': self.map.turn - 1,
            'winner': self.status['winner'],
            'status': self.status_record,
            'init-status': self.map.init_status,
            'record': self.map.record
        }

    def show(self, ui):
        self.map.show(ui)
        self.command.show(ui, self.map)
        self.scoreboard.show(ui)
