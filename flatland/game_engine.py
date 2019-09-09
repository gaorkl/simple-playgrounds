import pygame
from pygame.locals import K_q, KEYDOWN, KEYUP
from flatland.utils.config import *


class Engine():

    def __init__(self, playground, agents, rules, engine_parameters):

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

        # Display screen
        self.playground_img = None
        self.screen = pygame.display.set_mode((self.playground.width, self.playground.height))
        self.screen.set_alpha(None)

        # Rules TODO: add default dict
        self.replay_until_time_limit = rules.get('replay_until_time_limit', False)
        self.time_limit = rules.get('time_limit', 1000)

        # Engine parameters
        self.inner_simulation_steps = engine_parameters.get('simulation_steps', SIMULATION_STEPS)
        self.scale_factor = engine_parameters.get('scale_factor', 1)

        self.game_on = True
        self.current_elapsed_time = 0
        self.time = 0

        self.Q_ready_to_press = True

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

        for _ in range(self.inner_simulation_steps):
            self.playground.space.step(1. / self.inner_simulation_steps)

        for agent in self.agents:
            agent.health += (agent.reward - agent.energy_spent)

        self.playground.update_playground()

        # Termination

        if self.game_terminated():

            if self.replay_until_time_limit and self.time < self.time_limit:
                self.game_reset()

            else:
                self.game_on = False

        self.current_elapsed_time += 1
        self.time += 1

    def game_terminated(self):

        if self.time == self.time_limit:
            return True

        if not pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == False:
            self.Q_ready_to_press = True

        elif (pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == True) or self.playground.has_reached_termination:
            self.Q_ready_to_press = False

            return True

        return False


    def display_full_scene(self):

        img = self.playground.generate_playground_image()
        surf = pygame.surfarray.make_surface(img)
        self.screen.blit(surf, (0, 0), None)

        pygame.display.flip()

    def game_reset(self):

        self.current_elapsed_time = 0

        self.playground.remove_agents()
        self.playground.reset()

        for agent in self.agents:
            self.playground.add_agent(agent)
