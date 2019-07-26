

class SceneGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available scenes.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, scene_name):
        def decorator(subclass):
            cls.subclasses[scene_name] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, scene_name, params = {}):

        if scene_name not in cls.subclasses:
            raise ValueError('Scene type not implemented:' + scene_name)

        return cls.subclasses[scene_name](params)
