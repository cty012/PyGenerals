import json
import socket
from threading import Thread
import time

import back.sprites.component as c
import utils.fonts as f


class Scene:
    def __init__(self, args, server_ip, client):
        # arguments
        self.args = args
        self.mode = None
        self.server_ip = server_ip
        self.client = client

        # server and client
        print('CLIENT ENTER room...')
        self.id = None
        self.num = None
        self.thread = Thread(target=self.wait_info, name='wait-info')
        self.thread.start()

        # gui
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'back': c.Button(
                (self.args.size[0] // 2, 640), (600, 80), 'exit room',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
        }

    def process_events(self, events):
        if self.num == 0:
            return self.execute('back')
        if self.mode is not None and self.id is not None and self.num is not None:
            return self.execute('play')
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def wait_info(self):
        while self.num is None:
            try:
                length = int(json.loads(self.client.recv(10).decode('utf-8')))
                self.id, self.num = json.loads(self.client.recv(length).decode('utf-8'))
                if self.num == 0:
                    break
                print(f'\tyour id: {self.id}')
                print(f'\tplayer number: {self.num}')
            except socket.timeout:
                pass

    def execute(self, name):
        if name == 'play':
            print('CLIENT ENTER game...')
            return ['game', {'id': self.id, 'num': self.num, 'socket': self.client}]
        elif name == 'back':
            self.num = 0
            time.sleep(0.5)
            self.client.close()
            print('CLIENT EXIT room...')
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 100), f'IP: {self.server_ip}', f.cambria(60), color=(0, 0, 128), align=(1, 1))
        # TODO: show ip
        for name in self.buttons:
            self.buttons[name].show(ui)
