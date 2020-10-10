import back.players.replay_bot as rb
import back.sprites.modules.command as cm
import back.sprites.modules.map as m
import back.sprites.menus.replay_menu as rm
import back.sprites.modules.scoreboard as sb
import back.sprites.modules.turn_displayer as td


class Game:
    def __init__(self, args, replay):
        self.args = args
        self.replay = replay
        self.name = ''
        # display
        player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple'][:self.replay['num']]
        self.players = [{'land': 0, 'army': 0, 'color': player_colors[id]} for id in range(self.replay['num'])]
        self.scoreboard = sb.Scoreboard(self.args, (self.args.size[0] - 10, 10), self.players, align=(2, 0))
        self.replay_menu = rm.ReplayMenu((self.args.size[0] - 10, self.args.size[1] - 10), align=(2, 2))
        self.map = m.Map(
            self.args, self.args.get_pos(1, 1), self.players, 0, map_status=self.replay['init-status'], align=(1, 1))
        self.map.set_status({'visible': [True for _ in range(self.map.dim[0] * self.map.dim[1])]}, refresh=False)
        self.command = cm.Command(self.args, self.players, 0)
        self.player = rb.ReplayBot(self.args, self.map, self.replay['turn'])
        self.turn_displayer = td.TurnDisplayer(self.args, (10, 10), self.map, arrows=True, max_turn=self.replay['turn'])
        # status
        self.status = {'running': True}
        self.threshold = 0.5
        self.execute(['pause'])

    def process_events(self, events):
        # update map
        if self.map.clock.get_time() >= self.threshold:
            self.execute(['turn', self.map.turn + 1])
        if events['mouse-left'] == 'down':
            # process replay speed
            if self.replay_menu.in_range(events['mouse-pos']):
                return self.execute(self.replay_menu.process_click(events['mouse-pos']))
            # process turn displayer
            elif self.turn_displayer.in_range(events['mouse-pos']):
                return self.execute(self.turn_displayer.process_click(events['mouse-pos']))
        elif events['mouse-right'] == 'down':
            # process turn displayer
            if self.turn_displayer.in_range(events['mouse-pos']):
                return self.execute(self.turn_displayer.process_right_click(events['mouse-pos']))
        # process player moves
        player_commands = self.player.process_events(events)
        self.execute(['move-board', player_commands['move-board']])
        #
        if player_commands['turn'] != self.map.turn:
            self.execute(['turn', player_commands['turn']])
        if player_commands['speed'] is not None:
            self.execute(['speed', player_commands['speed']])
        if player_commands['pause']:
            command = self.replay_menu.buttons['pause'].text
            self.execute(['pause' if command == 'play' else command])
        return [None]

    def execute(self, command):
        if command[0] == 'pause':
            self.map.clock.toggle_run()
            self.replay_menu.toggle_pause()
        elif command[0] == 'quit':
            return ['quit']
        elif command[0] == 'speed':
            current_speed = int(self.replay_menu.buttons[""].text[6:])
            if command[1] == '+' and current_speed < 8:
                self.threshold /= 2
                self.replay_menu.buttons[''].text = f'speed×{current_speed * 2}'
            elif command[1] == '-' and current_speed > 1:
                self.threshold *= 2
                self.replay_menu.buttons[''].text = f'speed×{current_speed // 2}'
        elif command[0] == 'turn':
            if not 0 <= command[1] <= self.replay['turn']:
                return
            if self.map.clock.is_running():
                self.map.clock.clear()
                self.map.clock.start()
            else:
                self.map.clock.clear()
            self.map.turn = command[1]
            if self.replay['turn'] <= self.map.turn:
                self.map.clock.stop()
                self.replay_menu.buttons['pause'].text = 'replay'
                self.command.clear_commands()
            else:
                self.replay_menu.toggle_pause()
                self.replay_menu.toggle_pause()
                self.command.command_lists = [[item] for item in self.replay['record'][self.map.turn + 1]]
            self.map.set_status(self.replay['status'][self.map.turn], refresh=False)
            self.map.refresh(('player',))
        elif command[0] == 'replay':
            self.execute(['turn', 0])
            self.execute(['pause'])
        elif command[0] == 'move-board':
            self.map.move_board(command[1])
        elif command[0] == 'move-cursor':
            if command[1] != [0, 0]:
                self.map.move_cursor(command[1], None, execute=False)
        return [None]

    def show(self, ui):
        self.map.show(ui)
        self.command.show(ui, self.map, ids=range(self.replay['num']))
        self.scoreboard.show(ui)
        self.turn_displayer.show(ui)
        self.replay_menu.show(ui)
