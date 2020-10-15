class Human:
    def __init__(self, args, map):
        self.args = args
        self.type = 'human'
        self.map = map

    def process_events(self, events):
        key_pressed, key_down = events['key-pressed'], events['key-down']
        commands = {'move-board': [0, 0], 'move-cursor': [0, 0], 'clear': False}

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
                commands['move-cursor'][1] -= 1
            elif key == 'left':
                commands['move-cursor'][0] -= 1
            elif key == 'down':
                commands['move-cursor'][1] += 1
            elif key == 'right':
                commands['move-cursor'][0] += 1
            elif key == 'space':
                commands['clear'] = True
        if commands['move-cursor'][0] != 0 and commands['move-cursor'][1] != 0:
            commands['move-cursor'][1] = 0

        # mouse events
        if events['mouse-left'] == 'down':
            self.map.cursor = self.map.pos_to_cord(events['mouse-pos'])

        return commands
