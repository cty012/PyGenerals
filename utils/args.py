class Args:
    def __init__(self, scale=1):
        self.scale = scale
        self.size = (1280, 720)
        self.real_size = int(self.size[0] * scale), int(self.size[1] * scale)
