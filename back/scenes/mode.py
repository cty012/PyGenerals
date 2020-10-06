import socket

import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils


class Scene:
    def __init__(self, args):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'sing': c.Button(
                (self.args.size[0] // 2, 360), (600, 80), 'Single Player',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'mult': c.Button(
                (self.args.size[0] // 2, 460), (600, 80), 'Multi-Player',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2, 560), (600, 80), 'Back',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
        }

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def execute(self, name):
        if name == 'sing':
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', 5050))
            server.settimeout(1.0)
            server.listen()
            return ['game', {'id': 'server', 'num': 1, 'socket': server, 'clients': []}]
        elif name == 'mult':
            return ['game', {'id': 'server', 'num': 1, 'socket': None, 'clients': []}]
        elif name == 'back':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 150), "Game Mode", font=f.cambria(60), align=(1, 1))
        for name in self.buttons:
            self.buttons[name].show(ui)
