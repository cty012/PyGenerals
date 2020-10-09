import back.sprites.component as c
import utils.colors as cl
import utils.fonts as f
import utils.functions as utils


class TurnDisplayer:
    def __init__(self, args, pos, map, *, arrows=False, max_turn=0, align=(0, 0)):
        self.args = args
        self.arrows = arrows
        self.size = (160, 130) if self.arrows else (160, 60)
        self.pos = utils.top_left(pos, self.size, align=align)
        self.map = map
        self.min_turn = 0
        self.max_turn = max_turn
        self.buttons = {
            'turn-': c.Button(
                (self.pos[0] + self.size[0] // 2 - 40, self.pos[1] + 80),
                (30, 40), '', border=1, align=(1, 1), background=cl.gray_0),
            'turn+': c.Button(
                (self.pos[0] + self.size[0] // 2 + 40, self.pos[1] + 80),
                (30, 40), '', border=1, align=(1, 1), background=cl.gray_0)
        } if self.arrows else {}

    def in_range(self, pos):
        return self.pos[0] < pos[0] < self.pos[0] + self.size[0] and \
               self.pos[1] < pos[1] < self.pos[1] + self.size[1]

    def process_click(self, mouse_pos):
        for name in self.buttons:
            if self.buttons[name].in_range(mouse_pos):
                target_turn = eval(f'{self.map.turn} {name[4:]} 1')
                if self.min_turn <= target_turn <= self.max_turn:
                    return ['turn', target_turn]
        return [None]

    def process_right_click(self, mouse_pos):
        for name in self.buttons:
            if self.buttons[name].in_range(mouse_pos):
                target_turn = utils.min_max(eval(f'{self.map.turn} {name[4:]} 10'), self.min_turn, self.max_turn)
                return ['turn', target_turn]
        return [None]

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(self.pos, self.size, color=cl.white, pan=pan)
        ui.show_div(self.pos, self.size, border=1, pan=pan)
        ui.show_text(
            (self.pos[0] + 30, self.pos[1] + 30), f'Turn {self.map.turn}',
            f.get_font('quicksand', 22, 'otf'), save='turn', align=(0, 1), pan=pan)

        # arrows
        if self.arrows:
            # arrow div
            for name in self.buttons:
                self.buttons[name].show(ui)

            # arrows image
            color = (168, 168, 168) if self.map.turn <= self.min_turn else (0, 0, 0)
            ui.show_triangle((self.pos[0] + self.size[0] // 2 - 40, self.pos[1] + 80), 5, 'left', color=color)
            color = (168, 168, 168) if self.map.turn >= self.max_turn else (0, 0, 0)
            ui.show_triangle((self.pos[0] + self.size[0] // 2 + 40, self.pos[1] + 80), 5, 'right', color=color)
