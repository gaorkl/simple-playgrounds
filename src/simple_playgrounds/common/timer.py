from abc import ABC
from typing import Union, List, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.base.activable import Activable
    from simple_playgrounds.base.producer import Producer


class Timer(ABC):
    def __init__(self, timed_entity: Union[InteractiveElement, Producer]):

        self._running = False
        self._time = 0
        self._tic = False
        self._timed_entity = timed_entity

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def update(self):
        if self._running:
            self._time += 1

    def reset(self):
        self.stop()
        self._time = 0

    @property
    def timed_entity(self):
        return self._timed_entity


class CountDownTimer(Timer):
    def __init__(self, timed_entity, duration: int):

        super().__init__(timed_entity=timed_entity)
        self._duration = duration

    def update(self):
        super().update()

        if self._tic:
            self._tic = False
            self._timed_entity.activate()

        if self._time == self._duration:
            self.reset()
            self._tic = True


class PeriodicTimer(Timer):
    def __init__(self, timed_entity, durations: Union[List[int], int, Tuple[int, ...]]):

        if isinstance(durations, int):
            durations = [durations]

        assert isinstance(durations, (list, tuple))

        self._durations = durations
        self._current_duration = self._durations[0]
        self._index_duration = 0

        super().__init__(timed_entity=timed_entity)

    def reset(self):
        super().reset()
        self._index_duration = 0
        self._current_duration = self._durations[0]
        self._tic = False
        self.start()

    def update(self):

        super().update()

        if self._tic:
            self._tic = False
            self._timed_entity.activate()

        if self._time == self._current_duration:
            self._index_duration = (self._index_duration + 1) % len(
                self._durations)
            self._current_duration = self._durations[self._index_duration]

            self._time = 0
            self._tic = True
