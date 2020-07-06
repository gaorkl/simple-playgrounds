import pygame
from pygame.locals import K_q
from flatland.utils.config import *
from flatland.agents.sensors.sensor import SensorModality
from pygame.color import THECOLORS
import numpy
import time


class Engine():

    def __init__(self, playground, agents, rules = {}, engine_parameters = {}):

        '''
        Engine binds a playground, a list of agents, and rules of the game.

        :param playground: a Playground object where agents will play
        :param agents: a list of Agent objects
        :param rules: a dict with the rules of the game
        :param engine_parameters
        '''

        # Playground already exists
        self.playground = playground

        self.agents = agents
        for agent in self.agents:
            self.playground.add_agent(agent)

        # Rules
        self.replay_until_time_limit = rules.get('replay_until_time_limit', False)
        self.time_limit = rules.get('time_limit', 1000)

        # Engine parameters
        self.inner_simulation_steps = engine_parameters.get('inner_simulation_steps', SIMULATION_STEPS)
        self.display_mode = engine_parameters.get('display_mode', None)


        # Display screen
        self.need_command_display = False
        for agent in self.agents:
            if agent.controller and agent.controller.controller_type == 'keyboard':
                self.need_command_display = True

        if self.need_command_display:
           self.Q_ready_to_press = True

        # Screen for Pygame
        self.screen = pygame.display.set_mode((self.playground.width, self.playground.length))
        self.screen.set_alpha(None)

        # Screen for display
        self.surface_environment = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_sensors = pygame.Surface((self.playground.width, self.playground.length))

        self.game_on = True
        self.current_elapsed_time = 0
        self.total_elapsed_time = 0

        self.suface_environment_updated = False


    ###############
    # Draw top-down view for display

    def update_surface_environment(self):
        self.surface_environment.fill(THECOLORS["black"])

        for entity in self.playground.entities:
            entity.draw(self.surface_environment, draw_interaction=True)

        for agent in self.agents:
            agent.draw(self.surface_environment)


        self.suface_environment_updated = True

    def update_observations(self):

        # filter entities too far from sensors



        # Generate image only once if an agent has visual sensor
        # Do not draw elements that might be invisible to certain sensors
        if any([ agent.has_visual_sensor for agent in self.agents] ):
            self.surface_sensors.fill(THECOLORS["black"])

            # list all elements that might be invisible
            invisible_elements = []
            for agent in self.agents:
                for sensor in agent.sensors:
                    invisible_elements += sensor.invisible_elements

            for entity in self.playground.entities:
                if entity not in invisible_elements:
                    entity.draw(self.surface_sensors, draw_interaction=False)

            for agent in self.playground.agents:
                agent.draw(self.surface_sensors, excluded = invisible_elements)


        # Update sensors
        for agent in self.agents:

            # Draw other agents only once

            for sensor in agent.sensors:

                if sensor.sensor_modality is SensorModality.VISUAL:

                    # Draw body parts of agent which are visible to the sensor

                    surface_sensor = self.surface_sensors.copy()

                    for element in invisible_elements:
                        if element not in sensor.invisible_elements:
                            element.draw(surface_sensor)

                    img_sensor = pygame.surfarray.array3d(surface_sensor)
                    img_sensor = numpy.rot90(img_sensor, 1, (1, 0))
                    img_sensor = img_sensor[::-1, :, ::-1]

                    sensor.update_sensor(img_sensor)#, self.playground.entities, self.playground.agents)


                elif sensor.sensor_modality is SensorModality.GEOMETRIC:
                    entities = self.playground.entities
                    agents = self.playground.agents

                    sensor.update_sensor(agent, entities, agents)

                else:
                    raise ValueError


    def multiple_steps(self, actions, n_steps = 1):

        for stp in range(n_steps):
            self.step(actions)


    def step(self, actions):


        self.suface_environment_updated = False

        for agent in self.agents:
            agent.pre_step()
            agent.apply_actions_to_body_parts(actions[agent.name])

        for _ in range(self.inner_simulation_steps):
            self.playground.space.step(1. / self.inner_simulation_steps)

        # for agent in self.agents:
        #     agent.health += (agent.reward - agent.energy_spent)

        self.playground.update_playground()

        # Termination
        if self.game_terminated():

            if self.replay_until_time_limit and self.total_elapsed_time < self.time_limit:
                self.game_reset()

            else:
                self.game_on = False

        self.total_elapsed_time += 1
        self.current_elapsed_time += 1

    def game_terminated(self):

        if self.total_elapsed_time == self.time_limit:
            return True

        if self.playground.has_reached_termination:
            return True


        if self.need_command_display:
            if not pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == False:
                self.Q_ready_to_press = True

            elif (pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == True) :
                self.Q_ready_to_press = False
                return True

        return False

    # def generate_playground_image(self):
    #
    #     img = self.playground.generate_topdown_view(draw_interaction=True)
    #     return img

    def display_full_scene(self):

        if not self.suface_environment_updated:
            self.update_surface_environment()

        rot_surface = pygame.transform.rotate(self.surface_environment, 180)
        self.screen.blit(rot_surface, (0, 0), None)

        pygame.display.flip()

    def generate_topdown_image(self):

        if not self.suface_environment_updated:
            self.update_surface_environment()

        imgdata = pygame.surfarray.array3d(self.surface_environment)
        imgdata = numpy.rot90(imgdata, 1, (1, 0))
        imgdata = imgdata[::-1, :, ::-1]

        return imgdata

    def game_reset(self):


        self.current_elapsed_time = 0

        self.playground.remove_agents()
        self.playground.reset()

        for agent in self.agents:
            self.playground.add_agent(agent)

    def terminate(self):

        pygame.display.quit()
