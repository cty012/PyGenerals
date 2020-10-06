import json
import socket
from threading import Thread

import back.sprites.modules.map as m
from utils.parser import Parser


class Game:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.mode['num']]
        self.players = [{'num': 0, 'color': player_colors[id]} for id in range(self.mode['num'])]
        self.map = m.Map(self.args, self.args.get_pos(1, 1), self.players, self.mode['id'], align=(1, 1))
        # connect
        self.status = {'connected': True}
        self.thread_recv = []
        for i in range(1, self.mode['num']):
            new_thread = Thread(target=self.receive(i), name=f'recv-{i+1}', daemon=True)
            new_thread.start()
            self.thread_recv.append(new_thread)
        self.sends(json.dumps({'tag': 'init', 'status': self.map.get_status(('owner', 'num', 'terrain'))}))

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            pass
        # update map
        if self.map.clock.get_time() >= 0.5:
            self.map.update()
            self.sends(json.dumps({'tag': 'status', 'status': self.map.get_status()}))
            for id in range(1, self.mode['num']):
                self.send(json.dumps({'tag': 'commands', 'commands': self.map.commands[id]}), id)
        # process map moves
        map_commands = self.map.parse_events(events['key-pressed'], events['key-down'])
        if map_commands['clear']:
            self.map.clear_command(self.mode['id'])
        self.execute(['move-board', map_commands['move-board']])
        self.execute(['move-cursor', map_commands['move-cursor']])
        # process map
        self.execute(self.map.process_events(events))
        # pass
        return [None]

    def execute(self, command):
        if command[0] == 'pause':
            self.map.clock.toggle_run()
        elif command[0] == 'move-board':
            self.map.move_board(command[1])
        elif command[0] == 'move-cursor':
            if command[1] != [0, 0]:
                self.map.move_cursor(command[1])
        return [None]

    def send(self, msg, id):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            client = self.mode['clients'][id]
            client.send(msg_b_len_b)
            client.send(msg_b)
        except OSError as e:
            print(e)

    def sends(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            for client in self.mode['clients']:
                client.send(msg_b_len_b)
                client.send(msg_b)
        except OSError as e:
            print(e)

    def receive(self, id):
        def func():
            parser = Parser()
            client = self.mode['clients'][id-1]
            print(f'SERVER START receiving FROM CLIENT-{id}...')
            while self.status['connected']:
                # receive and parse msg
                try:
                    msg_strs = parser.parse(client.recv(1 << 20))
                except socket.timeout:
                    continue
                except json.decoder.JSONDecodeError:
                    print('\tJSON Decode Error!')
                    continue
                # deal with msg
                for msg_str in msg_strs:
                    msg = json.loads(msg_str)
                    if msg['tag'] == 'move':
                        self.map.commands[id].append((tuple(msg['move'][0]), tuple(msg['move'][1])))
                    elif msg['tag'] == 'clear':
                        self.map.clear_command(id)
            print(f'SERVER END receiving FROM CLIENT-{id}...')
        return func

    def show(self, ui):
        self.map.show(ui)
