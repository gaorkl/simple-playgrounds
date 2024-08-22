import math

from gymnasium import spaces

from spg.components.agents.attached import Arm
from spg.components.agents.base import ForwardContinuousAgent, StaticAgent
from spg.components.agents.interaction import GrasperHand, Trigger
from spg.components.agents.sensors.sensor.ray.ray import RaySensor
from spg.core.entity import Entity
from spg.core.entity.sprite import get_texture_from_geometry


class StaticAgentWithArm(StaticAgent):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(**kwargs)

        self.arm = Arm(rotation_range=math.pi / 4)
        self.add(self.arm, arm_position, arm_angle)


class StaticAgentWithTrigger(StaticAgentWithArm):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.trigger = Trigger()
        self.arm.add(self.trigger, (self.radius, 0))


class DynamicAgentWithArm(ForwardContinuousAgent):
    def __init__(self, arm_position, arm_angle, rotation_range, **kwargs):

        super().__init__(**kwargs)

        self.arm = Arm(rotation_range=rotation_range)
        self.add(self.arm, arm_position, arm_angle)


class DynamicAgentWithTrigger(DynamicAgentWithArm):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.trigger = Trigger()
        self.arm.add(self.trigger, (self.radius, 0))


class DynamicAgentWithGrasper(DynamicAgentWithArm):
    def __init__(self, arm_position, arm_angle, grasper_radius=10, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.grasper = GrasperHand(grasper_radius=grasper_radius, traversable=True)
        self.arm.add(self.grasper, (self.arm.radius, 0))


class MockRaySensor(Entity, RaySensor):
    def _convert_hitpoints_to_observation(self):
        return self._hitpoints

    def _get_ray_colors(self):
        pass

    def __init__(self, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=10, color=(255, 0, 0)
        )

        super().__init__(
            texture=texture,
            transparent=True,
            **kwargs,
        )

        RaySensor.__init__(self, **kwargs)

    @property
    def observation_space(self):
        return spaces.Box(low=0, high=255 + 255**2 + 255**3, shape=(13,))

    @property
    def attachment_point(self):
        return 0, 0
