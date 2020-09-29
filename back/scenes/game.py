import back.sprites.component as c


class Scene:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            pass
        return [None]

    def execute(self, name):
        return [None]

    def show(self, ui):
        self.background.show(ui)
