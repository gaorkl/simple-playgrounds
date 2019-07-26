

class PlaygroundGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available playgrounds.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, playground_name):
        def decorator(subclass):
            cls.subclasses[playground_name] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, playground_name, params = {}):

        if playground_name not in cls.subclasses:
            raise ValueError('Playground not implemented:' + playground_name)

        return cls.subclasses[playground_name](params)
