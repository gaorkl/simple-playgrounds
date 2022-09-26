from typing import List, Optional, Type, Union

from ..agent.communicator import Communicator
from ..agent.controller import Controller
from ..agent.device import Device
from ..agent.sensor import Sensor
from ..utils.definitions import CollisionTypes
from .element import ZoneElement


class Disabler(ZoneElement):
    def __init__(self, disable_cls: Union[List[Type[Device]], Type[Device]]):

        super().__init__(filename=":spg:platformer/tiles/area_forbidden.png")

        self._disable_cls = disable_cls

    @property
    def _collision_type(self):
        return CollisionTypes.DISABLER

    def disable(self, device: Device):

        if isinstance(device, self._disable_cls):
            device.disable()


class SensorDisabler(Disabler):
    def __init__(
        self, sensors: Optional[Union[List[Type[Sensor]], Type[Sensor]]] = None
    ):

        if not sensors:
            sensors = Sensor

        super().__init__(disable_cls=sensors)


class ControllerDisabler(Disabler):
    def __init__(
        self,
        controllers: Optional[Union[List[Type[Controller]], Type[Controller]]] = None,
    ):

        if not controllers:
            controllers = Controller

        super().__init__(disable_cls=controllers)


class CommunicatorDisabler(Disabler):
    def __init__(
        self,
        communicators: Optional[
            Union[List[Type[Communicator]], Type[Communicator]]
        ] = None,
    ):

        if not communicators:
            communicators = Communicator

        super().__init__(disable_cls=communicators)
