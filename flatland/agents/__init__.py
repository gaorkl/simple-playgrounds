from .agent import *

"""
TODO:
- documentation
- hamonize parameters settings:
   self.stuff = agent_params.get("stuff", default["stuff"])
   where default is a dict (cleverly named) defined in a config file

- clean the texture, add an arrow for the body_parts direction
- similarly for forward_head_agent : arrow for head direction

Maybe:
ABC, or registering, but it doesn't seem to be useful here

For fun and giggles:
Make an agent with base - arm - head

"""