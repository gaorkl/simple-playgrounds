from __future__ import annotations
from typing import Optional, Any, List, Tuple

from simple_playgrounds.common.entity import Entity
from simple_playgrounds.device.device import Device


class CommunicationDevice(Device):

    def __init__(self,
                 anchor: Entity,
                 transmission_range: Optional[float] = None,
                 receiver_capacity: Optional[int] = None,
                 ):
        """
        By default, Communication has infinite range and infinite receiver capacity.
        However, it can only send one message at a time.


        Args:
            anchor:
            transmission_range:
            receiver_capacity:
        """

        super().__init__(anchor=anchor)

        self._transmission_range = transmission_range
        self._receiver_capacity = receiver_capacity

        self._received_messages: List[Tuple[CommunicationDevice, Message]] = []
        self._comms_in_range: List[CommunicationDevice] = []

    def pre_step(self):
        super().pre_step()
        self.reset()
        self.update_list_comms_in_range()

    def reset(self):
        self._received_messages = []
        self._comms_in_range = []

    @property
    def position(self):
        return self._anchor.position

    @property
    def id(self):
        return self._anchor.name

    @property
    def transmission_range(self):
        return self._transmission_range

    @property
    def received_message(self):
        return self._received_messages

    def update_list_comms_in_range(self):

        comms = self._playground.communication_devices

        valid_comms = [com for com in comms if com is not self]

        for comm in valid_comms:
            if self.in_transmission_range(comm):
                self._comms_in_range.append(comm)

    @property
    def comms_in_range(self):
        return self._comms_in_range

    def in_transmission_range(self, comm: CommunicationDevice):

        dist = comm.position.get_distance(self.position)

        # If both have infinite range:
        if not (comm.transmission_range or self.transmission_range):
            return True

        # If only one has infinite range:
        elif (not comm.transmission_range) and self.transmission_range:
            if dist < self.transmission_range:
                return True

        elif comm.transmission_range and (not self.transmission_range):
            if dist < comm.transmission_range:
                return True

        elif dist < comm.transmission_range and dist < self.transmission_range:
            return True

        return False

    def send(self,
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
            self._received_messages.sort(key= (lambda s_m: self.position.get_distance(s_m[0].position)))
            if self._receiver_capacity:
                self._received_messages = self._received_messages[:self._receiver_capacity]


Message = Any
Communication = Tuple[CommunicationDevice, Message, Optional[CommunicationDevice]]
Stream = List[Communication]
