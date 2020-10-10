import os
import sys

import main.app as app
import utils.args as a


path = '.'
if getattr(sys, 'frozen', False):
    path = sys._MEIPASS
elif __file__:
    path = os.path.dirname(__file__)
print(path)

args = a.Args(scale=1, path=path)
app.launch(args)
