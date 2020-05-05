import pygame
from pygame.locals import K_q
from flatland.utils.config import *
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
            if agent.controller.controller_type == 'keyboard':
                self.need_command_display = True

        if self.need_command_display:
            self.command = pygame.display.set_mode((75, 75))
            self.Q_ready_to_press = True

        # Screen for Pygame
        self.screen = pygame.Surface((self.playground.length, self.playground.width))
        self.screen.set_alpha(None)

        self.game_on = True
        self.current_elapsed_time = 0
        self.total_elapsed_time = 0



    def update_observations(self):

        #Compute environment image once, then add agents when necessary
        self.playground.generate_entities_image()


        # For each agent, compute sensors
        for agent in self.agents:

            #data , arg = vision, geometric, class generator
            img = None
            entities = None
            agents = None

            if agent.has_visual_sensor:
                img = self.playground.generate_agent_image(sensor_agent = agent)

            if agent.has_geometric_sensor:
                entities = self.playground.entities
                agents = self.playground.agents

            agent.compute_sensors(img, entities, agents)


    # def apply_actions(self):
    #
    #     for agent in self.agents:
    #         agent.apply_action_to_physical_body()


    def multiple_steps(self, actions, n_steps = 1):

        for stp in range(n_steps):
            self.step(actions)


    def step(self, actions):

        for agent in self.agents:
            agent.pre_step()

            agent.apply_action_to_physical_body( actions[agent.name] )

        for _ in range(self.inner_simulation_steps):
            self.playground.space.step(1. / self.inner_simulation_steps)

        for agent in self.agents:
            agent.health += (agent.reward - agent.energy_spent)

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

        if self.current_elapsed_time == self.time_limit:
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

    def generate_playground_image(self):

        img = self.playground.generate_playground_image(draw_interaction=True)
        return img

    def display_full_scene(self):

        img = self.generate_playground_image()
        surf = pygame.surfarray.make_surface(img)
        self.screen.blit(surf, (0, 0), None)

        pygame.display.flip()

    def game_reset(self):


        self.current_elapsed_time = 0

        self.playground.remove_agents()
        self.playground.reset()

        for agent in self.agents:
            self.playground.add_agent(agent)

    def terminate(self):

        pygame.display.quit()
