from typing import Union, List, Tuple

from abc import ABC


class Timer(ABC):

    def __init__(self):

        self._running = False
        self._time = 0
        self._tic = False

    @property
    def tic(self):
        return self._tic

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


class CountDownTimer(Timer):

    def __init__(self, duration: int):

        super().__init__()
        self._duration = duration

    def step(self):
        super().step()

        if self._tic:
            self._tic = False

        if self._time == self._duration:
            self.reset()
            self._tic = True


class PeriodicTimer(Timer):

    def __init__(self,
                 durations: Union[List[int], int, Tuple[int, ...]]):

        if isinstance(durations, int):
            durations = [durations]

        assert isinstance(durations, (list, tuple))

        self._durations = durations
        self._current_duration = self._durations[0]
        self._index_duration = 0

        super().__init__()

    def reset(self):
        super().reset()
        self._index_duration = 0
        self._current_duration = self._durations[0]
        self._tic = False
        self.start()

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
