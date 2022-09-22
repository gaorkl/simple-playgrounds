from typing import List, Optional, Union

from ..agent.device import Device
from ..agent.sensor import Sensor
from ..utils.definitions import CollisionTypes
from .element import ZoneElement


class Disabler(ZoneElement):

    def __init__(self, disable_cls: Union[List[type[Device]], type[Device]]):

        super().__init__(filename=":spg:platformer/tiles/area_forbidden.png")

        self._disable_cls = disable_cls

    @property
    def _collision_type(self):
        return CollisionTypes.DISABLER

    def disable(self, device: Device):

        if isinstance(device, self._disable_cls):
            device.disable()


class SensorDisabler(Disabler):

    def __init__(self, sensors: Optional[Union[List[type[Sensor]], type[Sensor]]] = None):

        if not sensors:
            sensors = Sensor

        super().__init__(disable_cls=sensors)
