import back.sprites.component as c
import back.sprites.game_server as g_s
import back.sprites.game_client as g_c
import back.sprites.menus.game_menu as gm
import back.sprites.menus.saver as sv


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
        # game & game menu
        if self.mode['id'] == 0:
            self.game = g_s.Game(self.args, self.mode)
            self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), (300, 300), ('continue', 'save', 'quit'), align=(1, 1))
            self.saver = sv.Saver(self.args, self.game.name)
        else:
            self.game = g_c.Game(self.args, self.mode)
            self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), (300, 240), align=(1, 1))
            self.saver = sv.Saver(self.args, '')
        self.ended = False

    def process_events(self, events):
        # detect quit
        if not self.game.status['running']:
            return self.execute(['quit'])
        # detect end:
        if not self.ended and self.game.status['win'] is not None:
            self.ended = True
            self.execute(['pause'])
        # process save
        if self.saver.active:
            return self.execute(self.saver.process_events(events))
        # process menu
        if self.game_menu.active:
            return self.execute(self.game_menu.process_events(events))
        # process self
        if 'escape' in events['key-down']:
            return self.execute(['pause'])
        # process game
        self.game.process_events(events)
        return [None]

    def execute(self, command):
        if command[0] == 'pause':
            self.game_menu.active = not self.game_menu.active
            self.game.execute(['pause'])
        elif command[0] == 'save':
            self.saver.text = self.game.name
            self.saver.active = not self.saver.active
        elif command[0] == 'save-game':
            self.game.name = self.saver.text
            if self.mode['id'] == 0:
                self.saver.save(self.game.get_json())
            self.saver.active = not self.saver.active
        elif command[0] == 'close':
            self.game.execute(['close'])
        elif command[0] == 'quit':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
        # show game menu
        if self.game_menu.active:
            self.game_menu.show(ui, win=self.game.status['win'])
        # show game saver
        if self.saver.active:
            self.saver.show(ui)
