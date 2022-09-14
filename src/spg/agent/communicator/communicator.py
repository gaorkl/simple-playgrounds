from __future__ import annotations

from typing import Any, List, Optional, Tuple

from ...entity import EmbodiedEntity
from ..device import Device

Message = Any


class Communicator(Device):
    def __init__(
        self,
        anchor: EmbodiedEntity,
        transmission_range: Optional[float] = None,
        receiver_capacity: Optional[int] = None,
    ):
        """
        By default, Communicator has infinite range and infinite receiver capacity.
        However, it can only send one message at a time.


        Args:
            anchor:
            transmission_range:
            receiver_capacity:
        """

        super().__init__(anchor=anchor)

        self._transmission_range = transmission_range
        self._receiver_capacity = receiver_capacity

        self._received_messages: List[Tuple[Communicator, Message]] = []
        self._comms_in_range: List[Communicator] = []

    def pre_step(self):
        super().pre_step()
        self.reset()
        self.update_list_comms_in_range()

    def reset(self):
        self._received_messages = []
        self._comms_in_range = []

    @property
    def position(self):
        assert self._anchor
        return self._anchor.position

    @property
    def id(self):
        assert self._anchor
        return self._anchor.name

    @property
    def transmission_range(self):
        return self._transmission_range

    @property
    def received_message(self):
        return self._received_messages

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
        if not (comm.transmission_range or self.transmission_range):
            return True

        # If only one has infinite range:
        if (not comm.transmission_range) and self.transmission_range:
            if dist < self.transmission_range:
                return True

        elif comm.transmission_range and (not self.transmission_range):
            if dist < comm.transmission_range:
                return True

        elif dist < comm.transmission_range and dist < self.transmission_range:
            return True

        return False

    def send(
        self,
        msg: Message,
    ) -> Optional[Message]:

        if self._disabled:
            return None

        # Filter and Noise go here

        return msg

    def receive(self, sender, msg):

        if self._disabled or sender is self:
            return None

        if self.in_transmission_range(sender):
            self._received_messages.append((sender, msg))
            self._received_messages.sort(
                key=(lambda s_m: self.position.get_distance(s_m[0].position))
            )
            if self._receiver_capacity:
                self._received_messages = self._received_messages[
                    : self._receiver_capacity
                ]

        return None
