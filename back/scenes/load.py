import os
import re

import back.sprites.menus.saver as sv
import back.sprites.component as c
import utils.colors as cl
import utils.fonts as f
import utils.functions as utils


class Scene:
    def __init__(self, args):
        self.args = args

        # display
        self.bar_height = 100
        self.margin = 40
        self.padding = 20
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.pan = 0

        # saves and buttons
        if 'replay' not in os.listdir():
            os.mkdir('replay')
        self.saves = [SavedFile(file[:-4]) for file in os.listdir('replay') if file.endswith('.gnr')]
        self.saves.sort(key=lambda sf: [not sf.err, re.split(r'[\-_]', sf.date), sf.name], reverse=True)
        self.button = c.Button(
            (self.args.size[0] // 2, self.args.size[1] - self.bar_height // 2), (200, 50),
            'back', font=f.tnr(22), align=(1, 1), background=(210, 210, 210))

    def process_events(self, events):
        total_height = len(self.saves) * (self.padding + 120) - self.padding + 2 * self.margin
        if events['mouse-left'] == 'down':
            m_pos = events['mouse-pos']
            # back button
            if m_pos[1] >= self.args.size[1] - self.bar_height:
                if self.button.in_range(m_pos):
                    return ['menu']
            # saved files
            else:
                for i, saved_file in enumerate(self.saves):
                    pos = (self.args.size[0] // 2, self.margin + i * (self.padding + saved_file.size[1]) + self.pan)
                    if saved_file.in_range(pos, m_pos, align=(1, 0)):
                        return self.execute(saved_file.process_click(pos, m_pos, align=(1, 0)))
        elif events['mouse-wheel'] == 'up':
            self.pan += 30
            self.pan = min(self.pan, 0)
        elif events['mouse-wheel'] == 'down' and total_height > self.args.size[1] - self.bar_height:
            self.pan -= 30
            self.pan = max(self.pan, self.args.size[1] - self.bar_height - total_height)
        return [None]

    def execute(self, command):
        if command[0] == 'delete':
            os.remove(os.path.join('replay', f'{command[1]}.gnr'))
            for i in range(len(self.saves)):
                if self.saves[i].name == command[1]:
                    self.saves.pop(i)
                    break
        return command

    def show(self, ui):
        # background
        self.background.show(ui)
        # saves
        for i, saved_file in enumerate(self.saves):
            saved_file.show(
                ui, (self.args.size[0] // 2, self.margin + i * (self.padding + saved_file.size[1])),
                align=(1, 0), pan=(0, self.pan))
        # bar
        ui.show_div((0, self.args.size[1]), (self.args.size[0], self.bar_height), color=(46, 139, 87), align=(0, 2))
        ui.show_line((0, self.args.size[1] - self.bar_height), (self.args.size[0], self.args.size[1] - self.bar_height),
                     width=2)
        # button
        self.button.show(ui)


class SavedFile:
    def __init__(self, name):
        # display
        self.name = name
        self.size = (800, 120)
        self.player_colors = ['red', 'blue', 'green', 'yellow', 'brown', 'purple']

        # game
        self.replay = None
        self.date = ''
        self.num = 0
        self.turn = 0
        self.winner = None
        self.status = None
        self.init_status = None
        self.err = False
        try:
            self.replay = sv.Saver.load(self.name)
            self.date = self.replay['date']
            self.num = self.replay['num']
            self.turn = self.replay['turn']
            self.winner = self.replay['winner']
            self.status = self.replay['status']
            self.init_status = self.replay['init-status']
        except:
            print(f'ERROR loading saved file: {self.name}.gnr')
            self.err = True

    def in_range(self, b_pos, pos, *, align=(0, 0)):
        b_pos = utils.top_left(b_pos, self.size, align=align)
        return b_pos[0] < pos[0] < b_pos[0] + self.size[0] and b_pos[1] < pos[1] < b_pos[1] + self.size[1]

    def process_click(self, pos, mouse_pos, *, align=(0, 0)):
        pos = utils.top_left(pos, self.size, align=align)
        x0, x1, y0, y1, y2 = (
            pos[0] + self.size[0] - 120,
            pos[0] + self.size[0],
            pos[1],
            pos[1] + self.size[1] // 2,
            pos[1] + self.size[1])
        if x0 < mouse_pos[0] < x1 and y0 < mouse_pos[1] < y1:
            if not self.err:
                return ['replay', self.replay]
        elif x0 < mouse_pos[0] < x1 and y1 < mouse_pos[1] < y2:
            return ['delete', self.name]
        return [None]

    def show(self, ui, pos, *, align=(0, 0), pan=(0, 0)):
        pos = utils.top_left(pos, self.size, align=align)

        # show background:
        if self.err:
            color = cl.gray_1
        elif self.winner is None:
            color = cl.gray_0
        else:
            color = self.player_colors[self.winner]
        ui.show_div(pos, (15, self.size[1]), color=color, pan=pan)
        ui.show_div((pos[0] + 15, pos[1]), (self.size[0] - 15, self.size[1]), color=cl.gray_1, pan=pan)

        # show grid
        ui.show_div(pos, self.size, border=2, pan=pan)
        ui.show_line((pos[0] + self.size[0] - 300, pos[1]), (pos[0] + self.size[0] - 300, pos[1] + self.size[1]), pan=pan)
        ui.show_line((pos[0] + self.size[0] - 120, pos[1]), (pos[0] + self.size[0] - 120, pos[1] + self.size[1]), pan=pan)
        ui.show_line(
            (pos[0] + self.size[0] - 120, pos[1] + self.size[1] // 2),
            (pos[0] + self.size[0], pos[1] + self.size[1] // 2), pan=pan)

        # show name, num, & turn
        ui.show_text(
            (pos[0] + 40, pos[1] + self.size[1] // 2), self.name,
            f.cambria(22), save='load-name', align=(0, 1), pan=pan)
        if not self.err:
            ui.show_text(
                (pos[0] + self.size[0] - 210, pos[1] + self.size[1] // 2 - 18), f'Turn {self.turn}',
                f.cambria(20), save='load-info', align=(1, 1), pan=pan)
            ui.show_text(
                (pos[0] + self.size[0] - 210, pos[1] + self.size[1] // 2 + 18),
                f'{self.num} player' + ('' if self.num == 1 else 's'),
                f.cambria(20), save='load-info', align=(1, 1), pan=pan)

        # show play and delete images
        ui.show_img_by_path(
            (pos[0] + self.size[0] - 60, pos[1] + self.size[1] // 4), 'play.png', align=(1, 1), pan=pan)
        ui.show_img_by_path(
            (pos[0] + self.size[0] - 60, pos[1] + self.size[1] * 3 // 4), 'delete.png', align=(1, 1), pan=pan)
