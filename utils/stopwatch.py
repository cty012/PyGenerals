from typing import *
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

    def toggle_run(self):
        if self.is_running():
            self.stop()
        else:
            self.start()

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


class Stopwatch_dev:
    # MARK: Init
    def __init__(
            self,
            start_at: Union[int, float] = 0,
            run_speed: Union[int, float] = 1
            ) -> None:
        self.start_time: Union[int, float, None] = None
        self.interval: Union[int, float, None] = start_at
        self.run_speed: Union[int, float] = run_speed
        self.speed: Union[int, float] = 0

    def set_speed(self, speed: Union[int, float]) -> None:
        # Optimize: quit if speed does not change
        if speed == self.speed:
            return

        # Record uniform perf_counter time to minimize error
        now = time.perf_counter()

        # Catalog progress in previous speed
        if self.speed:
            self.interval = self.speed * (now - self.start_time)
            self.start_time = None

        # Set 'speed' attribute
        self.speed = speed

        # Convert back
        if self.speed:
            self.start_time = now - self.interval / self.speed
            self.interval = None
            self.run_speed = speed

    # MARK: Modifications
    def start(self, speed: Union[int, float] = ...) -> None:
        if not isinstance(speed, (int, float)):
            speed = self.run_speed
        self.set_speed(speed)

    def stop(self) -> None:
        self.set_speed(0)

    def toggle_run(self) -> None:
        if self.speed:
            self.set_speed(0)
        else:
            self.set_speed(self.run_speed)

    def clear(self) -> None:
        speed = self.speed
        self.set_speed(0)
        self.interval = 0
        self.set_speed(speed)

    # MARK: Queries
    def is_running(self) -> bool:
        return self.speed != 0

    def get_time(self) -> Union[int, float]:
        if self.speed:
            return self.speed * (time.perf_counter() - self.start_time)
        return self.interval

    def get_str_time(self) -> str:
        interval = self.get_time()
        minutes = int(interval) // 60
        seconds = int(interval) - minutes * 60
        decimals = int((interval - int(interval)) * 100)
        return f'{minutes:02}:{seconds:02}:{decimals:02}'
