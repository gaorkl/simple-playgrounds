"""
Scene elements that interact with an agent when they are in range.
Passive Scene Elements do not require action from an agent.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Tuple

from simple_playgrounds.common.definitions import ElementTypes, CollisionTypes
from simple_playgrounds.configs.parser import parse_configuration
from simple_playgrounds.element.element import SceneElement

from simple_playgrounds.device.device import Device
from simple_playgrounds.device.communication import CommunicationDevice
from simple_playgrounds.device.sensor import SensorDevice


class ModifierElement(SceneElement, ABC):
    """ Base Class for Modifier Elements.
    Modifier Elements modify properties of other elements."""

    def __init__(self,
                 config_key: Optional[Union[str, ElementTypes]] = None,
                 **entity_params):

        default_config = parse_configuration('element_modifier', config_key)
        entity_params = {**default_config, **entity_params}

        SceneElement.__init__(self,
                              visible_shape=False,
                              invisible_shape=True,
                              **entity_params)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.MODIFIER

    @abstractmethod
    def modify(self, modified):
        ...


###################
# Disabling Devices

class DeviceDisabler(ModifierElement, ABC):

    def __init__(self,
                 disabled_element_types: Union[type(Device), List[type(Device)]],
                 **entity_params):

        super().__init__(**entity_params)

        if isinstance(disabled_element_types, type(Device)):
            disabled_element_types = [disabled_element_types]

        self.disabled_cls: Tuple[type(Device)] = tuple(disabled_element_types)

    def modify(self, modified: Device):

        if isinstance(modified, self.disabled_cls):
            modified.disable()


class CommunicationDisabler(DeviceDisabler):

    def __init__(self, **entity_params):
        super().__init__(disabled_element_types=CommunicationDevice,
                         config_key=ElementTypes.COMM_DISABLER,
                         **entity_params)


class SensorDisabler(DeviceDisabler):
    def __init__(self,
                 disabled_sensor_types: Union[type(SensorDevice), List[type(SensorDevice)]],
                 **entity_params):

        super().__init__(disabled_element_types=disabled_sensor_types,
                         config_key=ElementTypes.SENSOR_DISABLER, **entity_params)
