import math
import random

from ..layouts import GridRooms, SingleRoom
from ..playground import PlaygroundRegister
from ...common.position_utils import CoordinateSampler, Trajectory
from ...common.timer import CountDownTimer, PeriodicTimer
from ...elements.collection.activable import Dispenser, VendingMachine, Chest, RewardOnActivation, OpenCloseSwitch, \
    TimerSwitch, Lock
from ...elements.collection.aura import Fairy, Fireball
from ...elements.collection.basic import Physical, Traversable
from ...elements.collection.conditioning import FlipReward
from ...elements.collection.contact import VisibleEndGoal, VisibleDeathTrap, Poison, Candy, ContactSwitch
from ...elements.collection.edible import Apple, RottenApple
from ...elements.collection.gem import Key, Coin
from ...elements.collection.teleport import VisibleBeamHoming, InvisibleBeam, Portal, PortalColor
from ...elements.collection.zone import DeathZone, GoalZone, HealingZone, ToxicZone
from ...elements.spawner import Spawner
from ...common.texture import RandomTilesTexture

from numpy.random import default_rng


@PlaygroundRegister.register('profiling', 'basic_unmovable')
class BasicUnmovable(SingleRoom):
    def __init__(self,
                 size,
                 n_elements_per_dim,
                 size_elements,
                 **playground_params):

        super().__init__(size=size, **playground_params)

        basic_cfg_keys = ['rectangle', 'square', 'pentagon', 'triangle', 'hexagon']

        for ind_x in range(n_elements_per_dim):
            for ind_y in range(n_elements_per_dim):

                coord_x = (1+ind_x) * size[0] / (n_elements_per_dim + 1)
                coord_y = (1+ind_x) * size[1] / (n_elements_per_dim + 1)
                orientation = random.uniform(0, 2*math.pi)

                cfg = random.choice(basic_cfg_keys)

                if cfg == 'rectangle':
                    element = Physical(config_key=cfg, name='test', size=(size_elements, size_elements))
                else:
                    element = Physical(config_key=cfg, name='test', radius=size_elements)

                self.add_element(element, initial_coordinates=((coord_x, coord_y), orientation))
