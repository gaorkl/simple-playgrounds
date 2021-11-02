# Implement tests for textures:
# Call with name, or instance, and apply size once asspciated with object.


from simple_playgrounds.common.texture import UniqueRandomTilesTexture
from simple_playgrounds.playground.layouts import GridRooms
from simple_playgrounds.engine import Engine


def test_wall_params_texture():

    custom_texture = UniqueRandomTilesTexture(color_min=(0, 100, 0),
                                          color_max=(250, 100, 0),
                                          n_colors=10)

    my_playground = GridRooms(size=(600, 600),
                          room_layout=(3, 3),
                          random_doorstep_position=False,
                          doorstep_size=80,
                          wall_texture= custom_texture)

    engine = Engine(time_limit=10000, playground=my_playground)
    engine.run()
    engine.terminate()