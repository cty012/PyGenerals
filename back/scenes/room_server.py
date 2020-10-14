import json
import socket
from threading import Thread

import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils


class Scene:
    def __init__(self, args):
        # arguments
        self.args = args

        # server and client
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(socket.gethostname())
        ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if utils.is_private_ip(ip)]
        self.ip = ips[0] if len(ips) > 0 else '127.0.0.1'
        self.server.bind((self.ip, 5051))
        self.server.settimeout(1.1)
        self.server.listen()

        self.clients = []  # {ip, port, client}
        self.status = {'running': True}
        self.thread = Thread(target=self.add_clients(self.status), name='add-clients', daemon=True)
        self.thread.start()

        # gui
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'play': c.Button(
                (self.args.size[0] // 2 - 300, 600), (300, 60), 'start game',
                font=f.tnr(23), save='tnr-23', align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2 + 300, 600), (300, 60), 'close room',
                font=f.tnr(23), save='tnr-23', align=(1, 1), background=(210, 210, 210)
            ),
        }

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        if 'return' in events['key-down']:
            return self.execute('play')
        return [None]

    def add_clients(self, status):
        def func():
            print('\nSERVER START accepting...')
            while status['running']:
                try:
                    client_socket, address = self.server.accept()
                    self.clients.append({'ip': address[0], 'port': address[1], 'socket': client_socket})
                    print(f'\tSERVER establish connection to {address}')
                except socket.timeout:
                    pass
            print('SERVER END accepting...')
        return func

    def execute(self, name):
        if name == 'play':
            self.status['running'] = False
            # send info to clients
            for i, client in enumerate(self.clients):
                client_info = bytes(json.dumps([i + 1, len(self.clients) + 1]), encoding='utf-8')
                client['socket'].send(bytes(f'{len(client_info):10}', encoding='utf-8'))
                client['socket'].send(client_info)
            return ['game', {
                'id': 0, 'num': len(self.clients) + 1, 'socket': self.server,
                'clients': self.clients
            }]
        elif name == 'back':
            self.close_client_sockets()
            self.status['running'] = False
            self.server.close()
            return ['menu']
        return [None]

    def close_client_sockets(self):
        for client in self.clients:
            info = bytes(json.dumps([{}, 0, 0]), encoding='utf-8')
            client['socket'].send(bytes(f'{len(info):10}', encoding='utf-8'))
            client['socket'].send(info)

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 100), f'IP: {self.ip}', f.cambria(60), color=(0, 0, 128), align=(1, 1))
        # show connected ips
        ui.show_text((self.args.size[0] // 2, 180), 'client ip', f.tnr(30), color=(128, 0, 0), align=(1, 1))
        for i, client in enumerate(self.clients):
            ui.show_text((self.args.size[0] // 2, 180 + (i + 1) * 60), client['ip'], f.tnr(30), align=(1, 1))
        # show buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
