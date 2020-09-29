import time


class Stopwatch:
    def __init__(self, start_time=0):
        self.start_time = None
        self.end_time = None
        self.speed = 1
        self.interval = start_time

    def start(self, speed=1):
        if self.start_time is None:
            self.start_time = time.time()
            self.speed = speed
        elif self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
            self.start_time = time.time()
            self.speed = speed
            self.end_time = None

    def set_speed(self, speed):
        if self.start_time is not None and self.end_time is not None:
            self.interval += self.speed * (self.end_time - self.start_time)
        elif self.start_time is not None and self.end_time is None:
            current = time.time()
            self.interval += self.speed * (current - self.start_time)
            self.start_time = current
        self.speed = speed

    def stop(self):
        if self.start_time is not None:
            self.end_time = time.time()

    def is_running(self):
        return self.start_time is not None and self.end_time is None

    def get_time(self):
        if self.start_time is not None and self.end_time is not None:
            return self.speed * (self.end_time - self.start_time) + self.interval
        elif self.start_time is not None and self.end_time is None:
            return self.speed * (time.time() - self.start_time) + self.interval

    def get_str_time(self):
        millis = self.get_time()
        minutes = int(millis) // 60
        seconds = int(millis) - minutes * 60
        decimals = int((millis - int(millis)) * 100)
        return f'{minutes:02}:{seconds:02}:{decimals:02}'

    def clear(self):
        self.start_time = None
        self.end_time = None
        self.interval = 0
