from typing import Union, List, Tuple

from abc import ABC


class Timer(ABC):

    def __init__(self):

        self._running = False
        self._time = 0

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def step(self):
        if self._running:
            self._time += 1

    def reset(self):
        self.stop()
        self._time = 0


class CountDown(Timer):

    def __init__(self, duration: int):

        super().__init__()
        self._duration = duration
        self._countdown_reached = False

    @property
    def countdown_reached(self):
        return self._countdown_reached

    def step(self):
        super().step()

        if self._countdown_reached:
            self._countdown_reached = False

        if self._time == self._duration:
            self.reset()
            self._countdown_reached = True


class PeriodicTics(Timer):

    def __init__(self,
                 durations: Union[List[int], int, Tuple[int, ...]]):

        if isinstance(durations, int):
            durations = [durations]

        assert isinstance(durations, (list, tuple))

        self._durations = durations
        self._current_duration = self._durations[0]
        self._index_duration = 0

        super().__init__()

        self.start()
        self._tic = False

    @property
    def tic(self):
        return self._tic

    def reset(self):
        super().reset()
        self._index_duration = 0
        self._current_duration = self._durations[0]
        self._tic = False

    def step(self):

        super().step()

        if self.tic:
            self._tic = False

        if self._time == self._current_duration:
            self._index_duration = (self._index_duration + 1) % len(
                self._durations)
            self._current_duration = self._durations[self._index_duration]

            self._time = 0
            self._tic = True
