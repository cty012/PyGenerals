import utils.colors as cl
import utils.fonts as f


class Human:
    def __init__(self, args, map):
        self.args = args
        self.type = 'human'
        self.map = map
        self.bookmarks = {str(i): None for i in range(1, 10)}
        self.bookmarks['1'] = self.map.get_base(self.map.id)

    def find_bookmark(self, grid):
        if grid is None:
            return None
        for index in self.bookmarks:
            if self.bookmarks[index] == grid:
                return index
        return None

    def process_events(self, events):
        commands = {'move-board': [0, 0, 11], 'move-cursor': [0, 0], 'clear': False, 'focus': None}

        # key events
        if events['mods'] & 1:
            commands['move-board'][2] = max(self.map.total_size)
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
            elif key == '0':
                commands['focus'] = self.map.cursor
            elif '1' <= key <= '9':
                if events['mods'] & 1:
                    orig_key = self.find_bookmark(self.map.cursor)
                    if orig_key is not None:
                        self.bookmarks[orig_key] = self.bookmarks[key]
                    self.bookmarks[key] = self.map.cursor
                else:
                    commands['focus'] = self.bookmarks[key]
        if commands['move-cursor'][0] != 0 and commands['move-cursor'][1] != 0:
            commands['move-cursor'][1] = 0

        # mouse events
        if events['mouse-left'] == 'down':
            self.map.cursor = self.map.pos_to_cord(events['mouse-pos'])

        return commands

    def show(self, ui, *, pan=(0, 0)):
        pan = (self.map.pos[0] + self.map.pan[0] + pan[0], self.map.pos[1] + self.map.pan[1] + pan[1])

        for index in self.bookmarks:
            if self.bookmarks[index] is None:
                continue
            grid = self.bookmarks[index]
            pos = (self.map.grid_size * grid[0], self.map.grid_size * grid[1])
            ui.show_div((pos[0] + 1, pos[1] + 1), (17, 11), pan=pan)
            ui.show_text(
                (pos[0] + 9, pos[1] + 6), index, f.get_font('quicksand-bold', 10, 'otf'),
                color=cl.white, save='bookmark', align=(1, 1), pan=pan)
