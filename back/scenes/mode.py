import back.sprites.component as c
import utils.fonts as f


class Scene:
    def __init__(self, args):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'sing': c.Button(
                (self.args.size[0] // 2, 360), (600, 80), 'Single Player',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'mult': c.Button(
                (self.args.size[0] // 2, 460), (600, 80), 'Multi-Player',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2, 560), (600, 80), 'Back',
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
        if name == 'sing':
            return ['game', {'open': 'new', 'mode': 'sing'}]
        elif name == 'mult':
            return ['game', {'open': 'new', 'mode': 'mult'}]
        elif name == 'back':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 150), "Game Mode", font=f.cambria(60), align=(1, 1))
        for name in self.buttons:
            self.buttons[name].show(ui)
