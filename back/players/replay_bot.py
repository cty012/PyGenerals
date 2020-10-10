import utils.functions as utils


class ReplayBot:
    def __init__(self, args, map, max_turn):
        self.args = args
        self.type = 'human'
        self.map = map
        self.min_turn = 0
        self.max_turn = max_turn

    def process_events(self, events):
        commands = {'move-board': [0, 0], 'turn': self.map.turn, 'speed': 0}

        # key events
        for key in events['key-pressed']:
            if key == 'w':
                commands['move-board'][1] -= 1
            elif key == 'a':
                commands['move-board'][0] -= 1
            elif key == 's':
                commands['move-board'][1] += 1
            elif key == 'd':
                commands['move-board'][0] += 1
        for key in events['key-down']:
            if key == 'up':
                commands['turn'] -= 10
            elif key == 'left':
                commands['turn'] -= 1
            elif key == 'down':
                commands['turn'] += 10
            elif key == 'right':
                commands['turn'] += 1
            elif key == '-':
                commands['speed'] -= 1
            elif key == '=':
                commands['speed'] += 1
        commands['turn'] = utils.min_max(commands['turn'], self.min_turn, self.max_turn)
        commands['speed'] = {0: None, -1: '-', 1: '+'}[commands['speed']]

        # mouse events
        if events['mouse-left'] == 'down':
            self.map.cursor = self.map.pos_to_cord(events['mouse-pos'])

        return commands
