import os
import platform
import sys

import main.app as app
import utils.args as a


path = '.'
save_path = '.'

if getattr(sys, 'frozen', False):
    import time
    t = time.time_ns()

    path = sys._MEIPASS
    save_path = os.path.join(os.path.expanduser('~'), '.PRISMSDeveloperSociety', 'pygenerals')
    try:
        os.makedirs(os.path.join(save_path, 'log'))
    except FileExistsError:
        pass
    try:
        os.makedirs(os.path.join(save_path, 'replay'))
    except FileExistsError:
        pass

    sys.stdout = open(os.path.join(save_path, 'log', f'{t}.log'), 'w')
    sys.stderr = sys.stdout

elif __file__:
    path = os.path.dirname(__file__)
    save_path = path

print(path)
print(save_path)

args = a.Args(scale=1, path=path, save_path=save_path)
app.launch(args)
