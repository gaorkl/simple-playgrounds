from simple_playgrounds.playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.elements.collection.basic import Physical

from simple_playgrounds.common.timer import CountDown, PeriodicTics


@PlaygroundRegister.register('test_test', 'basic')
class Basics(SingleRoom):
    def __init__(self):

        super().__init__(size=(200, 200))

        texture_obj = {'texture_type': 'color', 'color': [100, 220, 170]}

        obj_params = {
            'texture': texture_obj,
            'physical_shape': 'square',
            'radius': 22
        }

        self.my_obj = Physical(**obj_params)

        self.add_element(self.my_obj, ((150, 160), 0.2))


def test_new_object():

    pg = Basics()
    assert pg.my_obj.radius == 22


# Test Timers

def test_countdown():

    countdown = CountDown(6)
    assert not countdown.countdown_reached

    #################
    countdown.start()

    for i in range(5):
        countdown.step()
        assert not countdown.countdown_reached

    countdown.step()
    assert countdown.countdown_reached

    for i in range(10):
        countdown.step()
        assert not countdown.countdown_reached

    ################
    countdown.reset()
    countdown.start()

    for i in range(5):
        countdown.step()
        assert not countdown.countdown_reached

    countdown.step()
    assert countdown.countdown_reached

    countdown.step()
    assert not countdown.countdown_reached


def test_periodic_tics(periods):

    if isinstance(periods, int):
        periods = [periods]

    periodic_tics = PeriodicTics(durations=periods)

    for p in periods:

        for i in range(p-1):
            periodic_tics.step()
            assert not periodic_tics.tic

        periodic_tics.step()
        assert periodic_tics.tic

    for p in periods:

        for i in range(p - 1):
            periodic_tics.step()
            assert not periodic_tics.tic

        periodic_tics.step()
        assert periodic_tics.tic







