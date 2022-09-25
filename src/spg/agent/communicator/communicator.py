from __future__ import annotations

from typing import Any, List, Optional

from ..device import PocketDevice

Message = Any


COMM_COLOR = (123, 134, 13)


class Communicator(PocketDevice):
    def __init__(
        self,
        transmission_range: Optional[float] = None,
    ):
        """
        By default, Communicator has infinite range and infinite receiver capacity.
        However, it can only send one message at a time.


        Args:
            anchor:
            transmission_range:
            receiver_capacity:
        """

        super().__init__(color=COMM_COLOR)

        self._transmission_range = transmission_range

        self._comms_in_range: List[Communicator] = []

    def pre_step(self):
        super().pre_step()
        self.update_list_comms_in_range()

    def reset(self):
        self.pre_step()
        super().reset()

    @property
    def transmission_range(self):
        return self._transmission_range

    def update_list_comms_in_range(self):

        assert self._playground

        comms = []
        for agent in self._playground.agents:
            comms += agent.communicators

        valid_comms = [com for com in comms if com is not self]

        for comm in valid_comms:
            if self.in_transmission_range(comm):
                self._comms_in_range.append(comm)

    @property
    def comms_in_range(self):
        return self._comms_in_range

    def in_transmission_range(self, comm: Communicator):

        dist = comm.position.get_distance(self.position)

        # If both have infinite range:
        if not (comm.transmission_range or self._transmission_range):
            return True

        # If only one has infinite range:
        if (not comm.transmission_range) and self._transmission_range:
            if dist < self._transmission_range:
                return True

        elif comm.transmission_range and (not self._transmission_range):
            if dist < comm.transmission_range:
                return True

        elif dist < comm.transmission_range and dist < self._transmission_range:
            return True

        return False

    def send(
        self,
        msg: Message,
    ) -> Optional[Message]:

        if self._disabled:
            return None

        return msg

    def receive(self, sender, msg):

        if self._disabled or sender is self:
            return None

        if self.in_transmission_range(sender):
            return msg

        return None
