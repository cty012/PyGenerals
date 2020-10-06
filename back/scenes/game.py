import back.sprites.component as c
import back.sprites.game_server as g_s
# import back.sprites.game_client as g_c
import back.sprites.modules.game_menu as gm


class Scene:
    def __init__(self, args, mode):
        self.args = args
        # server: {'id': 0, 'num': <NUM OF PLAYERS>, 'socket': <SOCKET>, 'clients': [<CLIENT SOCKET>]}
        # client: {'id': >0, 'num': <NUM OF PLAYERS>, 'socket': <SOCKET>, 'server': <SERVER SOCKET>}
        self.mode = mode
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        # game menu
        self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), (300, 240), align=(1, 1))
        # game
        self.game = g_s.Game(self.args, self.mode)

    def process_events(self, events):
        # process menu
        if self.game_menu.activated:
            return self.execute(self.game_menu.process_events(events)[0])
        # process self
        if events['mouse-left'] == 'down':
            pass
        if 'escape' in events['key-down']:
            return self.execute('pause')
        # process game
        self.game.process_events(events)
        return [None]

    def execute(self, name):
        if name == 'pause':
            self.game_menu.activated = not self.game_menu.activated
        elif name == 'quit':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
        # show game menu
        if self.game_menu.activated:
            self.game_menu.show(ui)
