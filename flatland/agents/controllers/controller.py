
class ControllerGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available scene_layouts.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, controller_type):
        def decorator(subclass):
            cls.subclasses[controller_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, controller_type):

        if controller_type is None:
            raise ValueError('Controller not selected')

        if controller_type not in cls.subclasses:
            raise ValueError('Controller not implemented: ' + controller_type)

        return cls.subclasses[controller_type]()


class Controller():

    def __init__(self):

        self.require_key_mapping = False
        self.available_actions = {}
        self.actions = {}

    def get_actions(self):
        pass

    def set_available_actions(self, available_actions):
        self.available_actions = available_actions
        for act in available_actions:
            self.actions[act] = 0

    def get_empty_action_dict(self):

        actions = {}
        for a in self.available_actions:
            actions[a] = 0

        return actions

@ControllerGenerator.register_subclass('ai')
class AI(Controller):
    def __init__(self, controller_params):

        super().__init__(controller_params)



