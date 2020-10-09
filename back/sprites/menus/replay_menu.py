import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils


class ReplayMenu:
    def __init__(self, pos, *, size=(240, 200), align=(0, 0)):
        # display
        self.pos = utils.top_left(pos, size, align=align)
        self.size = size
        # buttons
        self.buttons = {
            'pause': c.Button(
                (self.pos[0] + self.size[0] // 2, self.pos[1] + 40), (180, 40), 'pause',
                font=f.tnr(22), border=1, save='tnr-22', align=(1, 1), background=(230, 230, 230)),
            'speed-': c.Button(
                (self.pos[0] + self.size[0] // 2 - 75, self.pos[1] + 100), (30, 40), '',
                font=f.tnr(22), border=1, save='tnr-22', align=(1, 1), background=(230, 230, 230)),
            '': c.Button(
                (self.pos[0] + self.size[0] // 2 - 1, self.pos[1] + 100), (123, 40), 'speed×1',
                font=f.tnr(22), border=1, save='tnr-22', align=(1, 1), background=(230, 230, 230)),
            'speed+': c.Button(
                (self.pos[0] + self.size[0] // 2 + 75, self.pos[1] + 100), (30, 40), '',
                font=f.tnr(22), border=1, save='tnr-22', align=(1, 1), background=(230, 230, 230)),
            'quit': c.Button(
                (self.pos[0] + self.size[0] // 2, self.pos[1] + 160), (180, 40), 'quit',
                font=f.tnr(22), border=1, save='tnr-22', align=(1, 1), background=(230, 230, 230)),
        }

    def in_range(self, pos):
        return self.pos[0] < pos[0] < self.pos[0] + self.size[0] and self.pos[1] < pos[1] < self.pos[1] + self.size[1]

    def process_click(self, pos):
        # buttons
        for name in self.buttons:
            if self.buttons[name].in_range(pos):
                if name in ['pause', 'quit']:
                    return [name]
                else:
                    return [name[:5], name[5:]]
        return [None]

    def toggle_pause(self):
        self.buttons['pause'].text = {'play': 'pause', 'pause': 'play'}[self.buttons['pause'].text]

    def show(self, ui, *, pan=(0, 0)):
        pos = self.pos[0] + pan[0], self.pos[1] + pan[1]
        # container
        ui.show_div(pos, self.size, color=(255, 255, 255))
        ui.show_div(pos, self.size, border=1)
        # buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
        # arrows
        color = (168, 168, 168) if self.buttons[''].text[-1:] == '1' else (0, 0, 0)
        ui.show_triangle((self.pos[0] + self.size[0] // 2 - 75, self.pos[1] + 100), 5, 'left', color=color)
        color = (168, 168, 168) if self.buttons[''].text[-1:] == '8' else (0, 0, 0)
        ui.show_triangle((self.pos[0] + self.size[0] // 2 + 75, self.pos[1] + 100), 5, 'right', color=color)
