from abc import ABC, abstractmethod
import math


class Entity(ABC):
    id_number = 0

    def __init__(self):
        """
        Instantiate an object with the following parameters:
        :param env: Game class, environment instantiating the object
        :param pos: 2d tuple or 'random', initial position of the object
        :param angle: float or 'random', initial orientation of the object
        :param body_parts: pymunk.Body, body_parts of the object in the instantiating environment
        :param texture: Texture class, texture of the shape of the object
        """

        # Initial body_parts, the real body_parts will be created by the environment
        self.body = None

        # Define initial position and orientation
        self.x = None
        self.y = None
        self.theta = None

        # Internal counter to assign identity number to each entity
        self.name_id = 'entity_'+str(Entity.id_number)
        Entity.id_number += 1

        # Basic properties
        self.absorbable = False
        self.movable = False
        self.actionable = False

        self.visible = True



    @property
    def x(self):
        if self.body is not None:
            return self.body.position[0]
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x
        if self.body is not None:
            self.body.position[0] = x


    @property
    def y(self):
        if self.body is not None:
            return self.body.position[1]
        return self.__y


    @y.setter
    def y(self, y):
        self.__y = y
        if self.body is not None:
            self.body.position[1] = y


    @property
    def theta(self):
        if self.body is not None:
            return (self.body.angle)%(2*math.pi)
        return self.__theta


    @theta.setter
    def theta(self, theta):
        self.__theta = theta
        if self.body is not None:
            self.body.angle = theta


    @abstractmethod
    def draw(self, surface):
        pass

