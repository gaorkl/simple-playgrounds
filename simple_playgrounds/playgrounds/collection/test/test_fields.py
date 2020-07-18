"""
Module containing playgrounds for testing Fields.
"""
from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.entities.field import Field
from simple_playgrounds.entities.scene_elements import Poison, Candy
from simple_playgrounds.utils.position_utils import PositionAreaSampler


class FieldsTest(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], width_length=[30, 100])
        field = Field(Poison, production_area=area_1)
        self.add_scene_element(field)

        area_2 = PositionAreaSampler(area_shape='rectangle', center=[200, 70], width_length=[50, 50])
        field = Field(Candy, production_area=area_2)
        self.add_scene_element(field)
