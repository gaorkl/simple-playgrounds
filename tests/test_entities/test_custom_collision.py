from spg.core.playground import EmptyPlayground
from spg.core.playground.manager.collision import get_colliding_entities
from tests.mock_interactives import ActivableMoving

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3
coord_far = (50, 50), 0


class CustomCollisionMoving(ActivableMoving):

    def __init__(self, collision_id, **kwargs):
        super().__init__(**kwargs)
        self.collision_type = collision_id
        self._set_pm_collision_type()
        self.activated_custom = False

    def activate_custom(self):
        self.activated_custom = True


def custom_handler(arbiter, space, data):
    data["activated"] = True

    activable_1, activable_2 = get_colliding_entities(data["playground"], arbiter)

    activable_1.activate_custom()
    activable_2.activate_custom()

    return True


def test_activable_element_activates_zone():
    playground = EmptyPlayground(size=(100, 100))

    new_collision_1 = playground.get_new_collision_type("COLLISION_1")
    new_collision_2 = playground.get_new_collision_type("COLLISION_2")

    playground.add_handler(new_collision_1, new_collision_2, custom_handler)

    ent_1 = CustomCollisionMoving(collision_id=new_collision_1)
    playground.add(ent_1, coord_center)

    ent_2 = CustomCollisionMoving(collision_id=new_collision_2)
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.activated_custom
    assert ent_2.activated_custom
