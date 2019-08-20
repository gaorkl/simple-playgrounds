import pygame
from pygame.locals import K_q
from flatland.utils.config import *

class Engine():

    def __init__(self, playground, agents, game_parameters):

        self.game_on = True
        self.agents = agents

        self.playground = playground

        self.agents_shape = {}

        for agent_name in self.agents:

            ag = self.agents[agent_name]['agent']
            self.playground.add_agent(agent_name, ag)

        self.playground_img = None

        self.screen = pygame.display.set_mode((self.playground.width, self.playground.height))
        self.screen.set_alpha(None)

    def update_observations(self):

        # Compute environment image once
        img = self.playground.generate_playground_image_sensor()

        # For each agent, compute sensors
        for agent_name in self.agents:

            self.agents[agent_name]['agent'].compute_sensors(img)

    def set_actions(self):

        for ag_name in self.agents:

            actions = self.agents[ag_name]['controller'].get_actions( )
            self.agents[ag_name]['agent'].apply_action(actions)

    def step(self):

        self.playground_img = None

        for ag in self.agents:
            self.agents[ag]['agent'].pre_step()

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

