from typing import Union, List, Tuple


class Timer(object):
    def __init__(self,
                 durations: Union[List[int], int, Tuple[int, ...]]):

        if isinstance(durations, int):
            durations = [durations]

        assert isinstance(durations, (list, tuple))

        self._durations = durations
        self.timer_done = False
        self._current_index_timer = 0
        self._timer = self._durations[self._current_index_timer]

    def reset(self):
        self._current_index_timer = 0
        self._timer = self._durations[self._current_index_timer]

    def step(self):

        self._timer -= 1

        if self.timer_done is True:
            self.timer_done = False

        if self._timer == 0:
            self._current_index_timer = (self._current_index_timer + 1) % len(
                self._durations)
            self._timer = self._durations[self._current_index_timer]

            self.timer_done = True
