import back.sprites.modules.map as m


class Game:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        # display
        self.map = m.Map(self.args, self.args.get_pos(1, 1), align=(1, 1))

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            pass
        if 'w' in events['key-pressed']:
            self.map.move_board(direction=(0, -1))
        if 'a' in events['key-pressed']:
            self.map.move_board(direction=(-1, 0))
        if 's' in events['key-pressed']:
            self.map.move_board(direction=(0, 1))
        if 'd' in events['key-pressed']:
            self.map.move_board(direction=(1, 0))
        return [None]

    def execute(self, name):
        return [None]

    def show(self, ui):
        self.map.show(ui)
