import json

import back.sprites.modules.map as m


class Game:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.mode['num']]
        self.players = [{'num': 0, 'color': player_colors[id]} for id in range(self.mode['num'])]
        self.map = m.Map(self.args, self.args.get_pos(1, 1), self.players, self.mode['id'], align=(1, 1))

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            pass
        # update map
        self.map.clear_commands()
        # process map moves
        map_commands = self.map.parse_events(events['key-pressed'], events['key-down'])
        self.execute(['move-board', map_commands['move-board']])
        self.execute(['move-cursor', map_commands['move-cursor']])
        # process map
        return self.execute(self.map.process_events(events))

    def execute(self, command):
        if command[0] == 'pause':
            self.map.clock.toggle_run()
        elif command[0] == 'move-board':
            self.map.move_board(command[1])
        elif command[0] == 'move-cursor':
            if command[1] != [0, 0]:
                move = self.map.move_cursor(command[1])
                if move is not None:
                    self.send(json.dumps({'tag': 'move', 'move': move}))
        return [None]

    def send(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        msg_b_len_b = bytes(f'{len(msg_b):10}', encoding='utf-8')
        try:
            for client in self.mode['clients']:
                client.send(msg_b_len_b)
                client.send(msg_b)
        except OSError as e:
            print(e)

    def show(self, ui):
        self.map.show(ui)
