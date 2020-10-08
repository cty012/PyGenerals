class Human:
    def __init__(self, args, map):
        self.args = args
        self.type = 'human'
        self.map = map

    def process_events(self, events):
        key_pressed, key_down = events['key-pressed'], events['key-down']
        commands = {'move-board': [0, 0], 'move-cursor': [0, 0], 'clear': False}

        # key events
        if 'w' in key_pressed:
            commands['move-board'][1] -= 1
        if 'a' in key_pressed:
            commands['move-board'][0] -= 1
        if 's' in key_pressed:
            commands['move-board'][1] += 1
        if 'd' in key_pressed:
            commands['move-board'][0] += 1
        if 'up' in key_down:
            commands['move-cursor'][1] -= 1
        if 'left' in key_down:
            commands['move-cursor'][0] -= 1
        if 'down' in key_down:
            commands['move-cursor'][1] += 1
        if 'right' in key_down:
            commands['move-cursor'][0] += 1
        if 'space' in key_down:
            commands['clear'] = True
        if commands['move-cursor'][0] != 0 and commands['move-cursor'][1] != 0:
            commands['move-cursor'][1] = 0

        # mouse events
        if events['mouse-left'] == 'down':
            target = self.map.pos_to_cord(events['mouse-pos'])
            if self.map.cursor is None or target not in self.map.get_adj_cords(self.map.cursor, corner=False, trim=False):
                self.map.cursor = target
            else:
                commands['move-cursor'] = [target[0] - self.map.cursor[0], target[1] - self.map.cursor[1]]

        return commands
