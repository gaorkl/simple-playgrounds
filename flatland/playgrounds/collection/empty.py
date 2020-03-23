from flatland.playgrounds.playground import PlaygroundGenerator, Playground

@PlaygroundGenerator.register_subclass('room')
class Room(Playground):

    def __init__(self, scene_params ):

        scene_params['scene_type'] = 'room'
        super(Room, self).__init__(scene_params)
