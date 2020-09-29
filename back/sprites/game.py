import back.sprites.component as c


class Game:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            pass
        return [None]

    def execute(self, name):
        return [None]

    def show(self, ui):
        pass
