import back.sprites.component as c
import utils.fonts as f


class Scene:
    def __init__(self, args):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'new': c.Button(
                (self.args.size[0] // 2, 360), (600, 80), 'New Game',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'join': c.Button(
                (self.args.size[0] // 2, 460), (600, 80), 'Join Game',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'quit': c.Button(
                (self.args.size[0] // 2, 560), (600, 80), 'Exit',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
        }

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def execute(self, name):
        if name == 'new':
            return ['level']
        elif name == 'join':
            return ['join']
        elif name == 'quit':
            return ['quit']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_texts(
            (self.args.size[0] // 2, 150), [["PY-", (128, 0, 0)], ["GENERALS", (0, 0, 128)]],
            font=f.cambria(120), align=(1, 1)
        )
        for name in self.buttons:
            self.buttons[name].show(ui)
