import back.sprites.component as c
import back.sprites.game_server as g_s
import back.sprites.game_client as g_c
import back.sprites.menus.game_menu as gm


class Scene:
    def __init__(self, args, mode):
        """
        mode:
        server: {
            'id': 0, 'ip', 'num': <NUM OF PLAYERS>, 'socket': <SOCKET>,
            'clients': {'ip': <CLIENT IP>, 'port': <CLIENT PORT>, 'socket': <CLIENT SOCKET>}
        }
        client: {'id': >0, 'ip', 'num': <NUM OF PLAYERS>, 'socket': <SOCKET>}
        """
        self.args = args
        self.mode = mode
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        # game menu
        self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), (300, 240), align=(1, 1))
        # game
        self.game = (g_s if self.mode['id'] == 0 else g_c).Game(self.args, self.mode)

    def process_events(self, events):
        # detect quit
        if not self.game.status['running']:
            return self.execute(['quit'])
        # process menu
        if self.game_menu.activated:
            return self.execute(self.game_menu.process_events(events))
        # process self
        if 'escape' in events['key-down']:
            return self.execute(['pause'])
        # process game
        self.game.process_events(events)
        return [None]

    def execute(self, command):
        if command[0] == 'pause':
            self.game_menu.activated = not self.game_menu.activated
            self.game.execute(['pause'])
        elif command[0] == 'close':
            self.game.execute(['close'])
        elif command[0] == 'quit':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
        # show game menu
        if self.game_menu.activated:
            self.game_menu.show(ui)
