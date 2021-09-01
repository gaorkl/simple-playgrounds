from typing import Optional, Dict, Union, List, Tuple
from abc import ABC, abstractmethod
from simple_playgrounds.agents.agent import Agent




class Sender(ABC):

    def __init__(self,
                 agent: Agent,
                 ):
        """
        By default, Sender have infinite range.

        Args:
            transmission_range:
        """

        self._agent = agent
        self._agents_in_range: List[Agent] = []

    def pre_step(self):

        self._agents_in_range = []


    @abstractmethod
    def send(self, *args) -> Dict[Agent, Message]:
        ...


class TargetedSender(Sender):

    def send(self, target: Agent, msg: Message):

        new_msg = msg.copy()

        if target in self._agents_in_range:
            return {target, new_msg}

        return {}


class BroadcastSender(Sender):

    def send(self, msg: Message):

        new_msg = msg.copy()

        dict_msg = {}

        for agent in self._agents_in_range:

            dict_msg[agent] = new_msg

        return dict_msg


class Receiver(ABC):

    def __init__(self,
                 agent: Agent):
        self._agent = agent

    @abstractmethod
    def filter_stream(self,
                      stream: Stream) -> Stream:
        ...

    def receive(self, stream: Stream):
        filtered_stream = self.filter_stream(stream)
        return filtered_stream


class ReceiverClosest(Receiver):

    def __init__(self,
                 agent: Agent,
                 receiver_capacity: int):

        super().__init__(agent)
        self._capacity = receiver_capacity

    def filter_stream(self, stream):

        list_stream = [(agent, msg) for agent, msg in stream.items()]
        list_stream.sort(key=lambda agent, msg: agent.position.get_distance(self._agent.position))
        filtered_list_stream = list_stream[:self._capacity]

        filtered_stream = {agent: msg for agent, msg in filtered_list_stream}

        return filtered_stream
