import re
import socket

import back.sprites.component as c
import utils.fonts as f
import utils.functions as utils
import utils.stopwatch as sw


class Scene:
    def __init__(self, args):
        # arguments
        self.args = args

        # regex
        self.regex = r'(([1-9]?[0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))'
        self.regex_one = r'^' + self.regex + r'\.?$'
        self.regex_two = r'^' + self.regex + r'\.' + self.regex + r'\.?$'
        self.regex_three = r'^(' + self.regex + r'\.){2}' + self.regex + r'\.?$'
        self.regex_full = r'^(' + self.regex + r'\.){3}' + self.regex + r'$'

        # socket
        self.server_ip = ''
        self.client = None
        self.init_socket()

        # gui
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.error_msg = None
        self.error_msg_clock = sw.Stopwatch()
        self.buttons = {
            'connect': c.Button(
                (self.args.size[0] // 2, 540), (400, 60), 'connect',
                font=f.tnr(22), align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2, 640), (400, 60), 'back',
                font=f.tnr(22), align=(1, 1), background=(210, 210, 210)
            ),
        }

    def init_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.settimeout(1.0)

    def process_events(self, events):
        # click button
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        # server_ip
        for key in events['key-down']:
            if key == 'return':
                return self.execute('connect')
            elif key not in self.possible():
                continue
            elif '0' <= key <= '9' or key == '.':
                self.server_ip += key
            elif key == 'backspace':
                self.server_ip = self.server_ip[:-1]
        # stopwatch
        if self.error_msg is not None and self.error_msg_clock.get_time() > 3:
            self.error_msg_clock.stop()
            self.error_msg_clock.clear()
            self.error_msg = None
        return [None]

    def possible(self):
        # dots: 0-2, last digits
        results = ['backspace']
        for char in [str(i) for i in range(10)] + ['.']:
            if any([
                re.match(reg, self.server_ip + char)
                for reg in [self.regex_one, self.regex_two, self.regex_three, self.regex_full]
            ]):
                results.append(char)
        return results

    def execute(self, name):
        if name == 'connect':
            if not utils.is_ip(self.server_ip):
                return [None]
            try:
                self.client.connect((self.server_ip, 5050))
                return ['room_client', self.server_ip, self.client]
            except socket.timeout:
                self.set_error_msg('Connection failed: Timeout')
                self.init_socket()
            except OSError as e:
                self.set_error_msg('Connection failed: Invalid address')
                print(e)
        elif name == 'back':
            self.client.close()
            return ['menu']
        return [None]

    def set_error_msg(self, msg):
        self.error_msg = msg
        self.error_msg_clock.clear()
        self.error_msg_clock.start()

    def show(self, ui):
        self.background.show(ui)
        # show input box
        ui.show_div((self.args.size[0] // 2, 300), (600, 80), color=(255, 255, 255), align=(1, 1))
        ui.show_div((self.args.size[0] // 2, 300), (600, 80), border=2, color=(0, 0, 0), align=(1, 1))
        ui.show_text((self.args.size[0] // 2, 300), self.server_ip, f.cambria(25), align=(1, 1))
        # show buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
        # show error message
        ui.show_text((self.args.size[0] // 2, 400), self.error_msg, f.tnr(20), color=(128, 0, 0), align=(1, 1))
