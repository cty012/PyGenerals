import back.sprites.component as c
import back.sprites.game_replay as g_r


class Scene:
    def __init__(self, args, replay):
        self.args = args
        self.replay = replay
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        # game & game menu
        self.game = g_r.Game(self.args, self.replay)
        self.ended = False

    def process_events(self, events):
        # detect quit
        if not self.game.status['running']:
            return self.execute(['quit'])
        # process game
        return self.execute(self.game.process_events(events))

    def execute(self, command):
        if command[0] == 'quit':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
