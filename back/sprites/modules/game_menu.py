import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils


class GameMenu:
    def __init__(self, args, pos, size, *, align=(0, 0)):
        self.args = args
        self.size = size
        self.pos = utils.top_left(pos, self.size, align=align)
        self.buttons = {
            'continue': c.Button(
                (self.pos[0] + self.size[0] // 2, self.pos[1] + 100), (200, 40), 'continue',
                font=f.tnr(22), align=(1, 0), background=(230, 230, 230)
            ),
            'quit': c.Button(
                (self.pos[0] + self.size[0] // 2, self.pos[1] + 160), (200, 40), 'quit',
                font=f.tnr(22), align=(1, 0), background=(230, 230, 230)
            )
        }
        self.activated = False

    def process_events(self, events):
        if not self.activated:
            return [None]
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        if 'escape' in events['key-down']:
            return self.execute('continue')
        return [None]

    def execute(self, name):
        if name == 'continue':
            return ['pause']
        elif name == 'quit':
            return ['quit']
        return [None]

    def show(self, ui, *, pan=(0, 0)):
        pos = self.pos[0] + pan[0], self.pos[1] + pan[1]
        # container
        ui.show_div(pos, self.size, color=(192, 192, 192))
        ui.show_div(pos, self.size, border=2)
        # msg
        ui.show_text((self.size[0] // 2, 40), f'PAUSED', f.cambria(28), align=(1, 0), pan=pos)
        # buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
