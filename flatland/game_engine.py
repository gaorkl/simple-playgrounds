import pygame
from pygame.locals import K_q
from flatland.utils.config import *
import time

class Engine():

    def __init__(self, playground, agents, game_parameters):

        '''
        Engine binds a playground, a list of agents, and rules of the game.

        :param playground: a Playground object where agents will play
        :param agents: a list of Agent objects
        :param game_parameters: a dict with the parameters of the game
        '''

        # Playground already exists
        self.playground = playground

        self.agents = agents
        for agent in self.agents:
            self.playground.add_agent(agent)

        # Display screen
        self.playground_img = None
        self.screen = pygame.display.set_mode((self.playground.width, self.playground.height))
        self.screen.set_alpha(None)

        # Rules
        self.game_on = True


    def update_observations(self):

        # Compute environment image once

        img = self.playground.generate_playground_image_sensor()

        # For each agent, compute sensors
        for agent in self.agents:

            agent.compute_sensors(img)


    def set_actions(self):

        for agent in self.agents:

            agent.get_actions()
            agent.apply_action()

    def step(self):

        self.playground_img = None

        for agent in self.agents:
            agent.pre_step()

        for _ in range(SIMULATION_STEPS):
            self.playground.space.step(1. / SIMULATION_STEPS)

        if pygame.key.get_pressed()[K_q]:
            self.game_on = False

        self.playground.update_playground()

    def display_full_scene(self):

        img = self.playground.generate_playground_image()
        surf = pygame.surfarray.make_surface(img)
        self.screen.blit( surf , (0,0), None)

        pygame.display.flip()

