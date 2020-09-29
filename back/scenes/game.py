import back.sprites.component as c
import back.sprites.modules.game_menu as gm


class Scene:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        # game menu
        self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), (300, 240), align=(1, 1))
        # game
        self.game = None

    def process_events(self, events):
        if self.game_menu.activated:
            return self.execute(self.game_menu.process_events(events)[0])
        if events['mouse-left'] == 'down':
            pass
        if 'escape' in events['key-down']:
            return self.execute('pause')
        return [None]

    def execute(self, name):
        if name == 'pause':
            self.game_menu.activated = not self.game_menu.activated
        elif name == 'quit':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        # show game menu
        if self.game_menu.activated:
            self.game_menu.show(ui)
