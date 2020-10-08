import json
import os
import re

import back.sprites.component as c
import utils.colors as cl
import utils.fonts as f
import utils.functions as utils


class Saver:
    def __init__(self, args, text='', *, size=(600, 300), input_size=(500, 50)):
        self.args = args

        # display
        self.active = False
        self.size = size
        self.input_size = input_size
        self.color = (192, 192, 192)

        # text
        self.text = text
        self.regex = '^[a-z0-9_\\-]$'

        # buttons
        self.buttons = {
            'save': c.Button(
                (self.args.size[0] // 2 - 100, self.args.size[1] // 2 + 100), (140, 40), 'save',
                font=f.tnr(22), border=1, align=(1, 1), background=cl.white),
            'back': c.Button(
                (self.args.size[0] // 2 + 100, self.args.size[1] // 2 + 100), (140, 40), 'back',
                font=f.tnr(22), border=1, align=(1, 1), background=cl.white)
        }

    def process_events(self, events):
        # key events
        for key in events['key-down']:
            if len(self.text) < 20 and re.match(self.regex, key):
                self.text += self.shift(key, events['mods'])
            elif key == 'backspace':
                self.text = self.text[:-1]
            elif key == 'escape':
                return self.execute('back')
            elif key == 'return' and len(self.text) > 0:
                return self.execute('save')
        # mouse click events
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def execute(self, name):
        if name == 'save':
            return ['save-game']
        elif name == 'back':
            return ['save']
        return [None]

    def save(self, game_json):
        if 'replay' not in os.listdir():
            os.mkdir('replay')
        with open(os.path.join('replay', f'{self.text}.gnr'), 'w') as file:
            json.dump(game_json, file)

    @classmethod
    def load(cls, name):
        with open(os.path.join('replay', f'{name}.gnr'), 'r') as file:
            content = json.load(file)
        return content

    def shift(self, key, mods):
        if mods & 64 != 0 or mods & 128 != 0:
            return '_' if key == '-' else key.capitalize()
        return key

    def show(self, ui):
        if self.active:
            center = (self.args.size[0] // 2, self.args.size[1] // 2)
            # show container
            ui.show_div(center, self.size, color=self.color, align=(1, 1))
            ui.show_div(center, self.size, border=1, align=(1, 1))
            # show title
            ui.show_text((center[0], center[1] - 100), 'SAVE REPLAY', font=f.tnr(30), align=(1, 1))
            # show input area
            ui.show_div((center[0], center[1] - 15), self.input_size, color=(255, 255, 255), align=(1, 1))
            ui.show_div((center[0], center[1] - 15), self.input_size, border=1, align=(1, 1))
            corner = utils.top_left((center[0], center[1] - 15), self.input_size, align=(1, 1))
            ui.show_text((corner[0] + 20, corner[1] + 14), self.text, font=f.tnr(22))
            # show buttons
            for name in self.buttons:
                self.buttons[name].show(ui)
