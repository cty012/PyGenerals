import os
import pygame


class Font:
    def __init__(self):
        self.root = os.path.join('.', 'src', 'fonts')

    def render_font(self, font):
        if font[0] == 'ttf':
            return pygame.font.Font(font[1], font[2])
        elif font[0] == 'src':
            return pygame.font.Font(self.get(font[1]), font[2])
        elif font[0] == 'sys':
            return pygame.font.SysFont(font[1], font[2])

    def get(self, file):
        return os.path.join(self.root, file)
