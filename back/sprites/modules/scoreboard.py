import utils.colors as c
import utils.fonts as f
import utils.functions as utils


class Scoreboard:
    def __init__(self, args, pos, players, *, align=(0, 0)):
        self.args = args
        self.size = (250, 40 * (len(players) + 1))
        self.pos = utils.top_left(pos, self.size, align=align)
        self.players = players

    def in_range(self, pos):
        return self.pos[0] < pos[0] < self.pos[0] + self.size[0] and \
               self.pos[1] < pos[1] < self.pos[1] + self.size[1]

    def process_mouse_events(self, mouse_pos):
        return [None]

    def show(self, ui, *, pan=(0, 0)):
        # background
        ui.show_div(self.pos, self.size, color=c.white, pan=pan)
        x, y = self.pos
        # header
        ui.show_text(
            (x + (self.size[0] - 120) // 2, y + 20), 'Player', font=f.get_font('quicksand', 18, 'otf'),
            color=c.black, save='scoreboard-header', align=(1, 1), pan=pan)
        ui.show_text(
            (x + self.size[0] - 90, y + 20), 'Army', font=f.get_font('quicksand', 18, 'otf'),
            color=c.black, save='scoreboard-header', align=(1, 1), pan=pan)
        ui.show_text(
            (x + self.size[0] - 30, y + 20), 'Land', font=f.get_font('quicksand', 18, 'otf'),
            color=c.black, save='scoreboard-header', align=(1, 1), pan=pan)
        # player info & horizontal grid
        for id in range(len(self.players)):
            y += 40
            ui.show_div((x, y), (self.size[0] - 120, 40), color=self.players[id]['color'], pan=pan)
            ui.show_line((x, y), (x + self.size[0], y), pan=pan)
            ui.show_text(
                (x + (self.size[0] - 120) // 2, y + 20), str(id), font=f.get_font('quicksand-bold', 20, 'otf'),
                color=c.white, save='scoreboard-name', align=(1, 1), pan=pan)
            ui.show_text(
                (x + self.size[0] - 90, y + 20), str(self.players[id]['army']),
                font=f.get_font('quicksand', 18, 'otf'), color=c.black, save='scoreboard-num', align=(1, 1), pan=pan)
            ui.show_text(
                (x + self.size[0] - 30, y + 20), str(self.players[id]['land']),
                font=f.get_font('quicksand', 18, 'otf'), color=c.black, save='scoreboard-num', align=(1, 1), pan=pan)
        # vertical grid
        ui.show_line(
            (self.pos[0] + self.size[0] - 120, self.pos[1]),
            (self.pos[0] + self.size[0] - 120, self.pos[1] + self.size[1]), pan=pan)
        ui.show_line(
            (self.pos[0] + self.size[0] - 60, self.pos[1]),
            (self.pos[0] + self.size[0] - 60, self.pos[1] + self.size[1]), pan=pan)
        # edge
        ui.show_div(self.pos, self.size, border=1, pan=pan)
