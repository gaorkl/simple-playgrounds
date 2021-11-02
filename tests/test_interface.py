from simple_playgrounds.playground.playground import PlaygroundRegister
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.element.elements.basic import Physical

from simple_playgrounds.common.timer import CountDownTimer, PeriodicTimer


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

####################
# Test Timers


def test_countdown():

    countdown = CountDownTimer(6)
    assert not countdown.tic

    #################
    countdown.start()

    for i in range(5):
        countdown.step()
        assert not countdown.tic

    countdown.step()
    assert countdown.tic

    for i in range(10):
        countdown.step()
        assert not countdown.tic

    ################
    countdown.reset()
    countdown.start()

    for i in range(5):
        countdown.step()
        assert not countdown.tic

    countdown.step()
    assert countdown.tic

    countdown.step()
    assert not countdown.tic


def test_periodic_tics(periods):

    if isinstance(periods, int):
        periods = [periods]

    periodic_tics = PeriodicTimer(durations=periods)
    periodic_tics.reset()

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







