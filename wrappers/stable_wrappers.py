import gym
from gym import spaces
from simple_playgrounds.utils import ActionTypes, SensorModality
from simple_playgrounds import Engine
import numpy

import tensorflow as tf
from stable_baselines.common.policies import LstmPolicy, CnnLstmPolicy, CnnLnLstmPolicy, CnnPolicy



class PlaygroundEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, playground, agent, continuous_action_space = True):
        """
        Args:
            game_engine: Engine to run the

        """

        super().__init__()

        self.game = Engine(playground, replay=False, screen=False)

        self.agent = agent

        assert self.agent in self.game.agents

        # Define action space

        actions = self.agent.get_all_available_actions()

        self.continuous_action_space = continuous_action_space

        self.actions_dict = {}

        if self.continuous_action_space:

            lows = []
            highs = []

            for action in actions:
                lows.append(action.min)
                highs.append(action.max)

                if action.body_part not in self.actions_dict:
                    self.actions_dict[action.body_part] = {}

                if action.action not in self.actions_dict[action.body_part]:
                    self.actions_dict[action.body_part][action.action] = 0

            self.action_space = spaces.Box(low=numpy.array(lows), high=numpy.array(highs))

        else:

            dims = []

            for action in actions:
                if action.action_type is ActionTypes.DISCRETE:
                    dims.append(2)
                elif action.action_type is ActionTypes.CONTINUOUS_CENTERED:
                    dims.append(3)
                elif action.action_type is ActionTypes.CONTINUOUS_NOT_CENTERED:
                    dims.append(2)

            self.action_space = spaces.MultiDiscrete(dims)

        # Define observation space

        # Normalize all sensors to make sure they are in the same range
        width_all_sensors, height_all_sensors = 0, 0
        for sensor in self.agent.sensors:

            if sensor.sensor_modality is SensorModality.SEMANTIC:
                raise ValueError( 'Semantic sensors not supported')
            sensor.normalize = True

            if isinstance(sensor.shape, int):
                width_all_sensors = max(width_all_sensors, sensor.shape)
                height_all_sensors += 1

            elif len(sensor.shape) == 2:
                width_all_sensors = max(width_all_sensors, sensor.shape[0])
                height_all_sensors += 1

            else:
                width_all_sensors = max(width_all_sensors, sensor.shape[0])
                height_all_sensors += sensor.shape[1]

        self.observation_space = spaces.Box(low=0, high=1, shape=(height_all_sensors, width_all_sensors, 3), dtype=numpy.float32)
        self.observations = numpy.zeros((height_all_sensors, width_all_sensors, 3))

        self.n_steps = game_engine.playground.time_limit


    def step(self, action):

        # First, send actions to game engint

        actions_to_game_engine = {}

        # Convert Stable-baselines actions into game engine actions
        for index_action, available_action in enumerate(self.agent.get_all_available_actions()):

            body_part = available_action.body_part
            action_ = available_action.action
            action_type = available_action.action_type

            converted_action = action[index_action]

            # convert discrete action to binry
            if self.continuous_action_space and action_type is ActionTypes.DISCRETE:
                converted_action = 0 if converted_action < 0.5 else 1

            # convert continuous actions in [-1, 1]
            elif not self.continuous_action_space and action_type is ActionTypes.CONTINUOUS_CENTERED:
                converted_action = converted_action - 1

            self.actions_dict[body_part][action_] = converted_action

        actions_to_game_engine[self.agent.name] = self.actions_dict

        # Generate actions for other agents
        for agent in self.game.agents:
            if agent is not self.agent:
                actions_to_game_engine[agent.name] = agent.controller.generate_actions()

        # Now that we have all ctions, run the engine, and get the observations
        self.game.step(actions_to_game_engine)
        self.game.update_observations()

        # Concatenate the observations in a format that stable-baselines understands

        current_height = 0
        for sensor in self.agent.sensors:

            if isinstance(sensor.shape, int):
                self.observations[current_height, :sensor.shape, 0] = sensor.sensor_value[:]
                current_height += 1

            elif len(sensor.shape) == 2:
                self.observations[current_height, :sensor.shape[0], :] = sensor.sensor_value[:, :]
                current_height += 1

            else:
                self.observations[:sensor.shape[0], :sensor.shape[1], :] = sensor.sensor_value[:, :, :]
                current_height += sensor.shape[0]


        reward = self.agent.reward

        if self.game.playground.done:
            done = True

        elif not self.game.game_on:
            done = True
        else:
            done = False

        return (self.observations, reward, done, {})


    def reset(self):

        #     if self.is_relaxing:
        #         self.game.playground.params['n_pellets'] = self.game.playground.params['n_pellets'] * self.relax

        self.game.reset()
        self.game.total_elapsed_time = 0

        #state, rewards, done, _ = self.step(self.action_space.sample())

        return numpy.zeros(self.observations.shape)

    def render(self, mode='human'):
        img = self.game.generate_topdown_image()
        return img

    def close(self):
        self.game.terminate()



def make_vector_env(playground, agent):
    """
    Utility function for multiprocessed env.

    Args:
        pg: Instance of a Playground
        Ag: Agent
    """
    def _init():

        playground.add_agent(agent)
        custom_env = PlaygroundEnv(playground, agent, continuous_action_space=True)

        return custom_env

    return _init


class CustomPolicy(CnnLnLstmPolicy):


    def __init__(self, *args, **_kwargs):

        activ = 'selu'

        self.custom_layers = []
        self.observation_shape = _kwargs['observation_shape']


        with tf.variable_scope("model"):

            for shape in self.observation_shape:

                height, width, channel = shape

                if height == 1:

                    conv_1 = tf.keras.layers.Conv1D(filters=64, kernel_size=8, strides=4, activation=activ)
                    conv_2 = tf.keras.layers.Conv1D(filters=32, kernel_size=4, strides=2, activation=activ)
                    conv_3 = tf.keras.layers.Conv1D(filters=32, kernel_size=3, strides=1, activation=activ)


                else:

                    conv_1 = tf.keras.layers.Conv2D(filters=64, kernel_size=8, strides=(4, 4), activation=activ)
                    conv_2 = tf.keras.layers.Conv2D(filters=32, kernel_size=4, strides=(2, 2), activation=activ)
                    conv_3 = tf.keras.layers.Conv1D(filters=32, kernel_size=3, strides=(1,1), activation=activ)

                flat = tf.keras.layers.Flatten()
                dense = tf.keras.layers.Dense(units=128, activation=activ)

                self.custom_layers.append([conv_1, conv_2, conv_3, flat, dense])

            self.dense_all_1 = tf.keras.layers.Dense(units=64, activation=activ)
            self.dense_all_2 = tf.keras.layers.Dense(units=32, activation=activ)

        super(CustomPolicy, self).__init__(*args, n_lstm=64, cnn_extractor=self.feature_extractor, **_kwargs)


    def feature_extractor(self, input_observations, **kwargs):

        current_height = 0

        features = []

        for index_observation, shape in enumerate(self.observation_shape):

            height, width, channel = shape

            obs = input_observations[:, current_height: current_height + height, :width, :channel]
            if height == 1:
                obs = tf.squeeze(obs, 1 )

            current_height+=height

            conv_1, conv_2, conv_3, flat, dense = self.custom_layers[index_observation]

            h_1 = conv_1(obs)
            h_1 = tf.keras.layers.Dropout(rate=0.1)(h_1)

            h_2 = conv_2(h_1)
            h_2 = tf.keras.layers.Dropout(rate=0.1)(h_2)

            h_3 = conv_3(h_2)
            h_3 = tf.keras.layers.Dropout(rate=0.1)(h_3)

            h_flat = flat(h_3)
            h_dense = dense(h_flat)
            h_dense = tf.keras.layers.Dropout(rate=0.1)(h_dense)

            features.append(h_dense)

        h_concat =  tf.concat( features, axis=1 )

        h_out_1 = self.dense_all_1(h_concat)

        return self.dense_all_2(h_out_1)


