# Checkpoints for easy rewind
#       self._checkpoints: Dict[Timestep, bytes] = {}
#       self._actions: Dict[Timestep, Tuple[AgentCommandsDict, AgentMessagesDict]] = {}

# Make checkpoints a decorator?


#  ################
#   # Checkpoints
#   ################

#   def save_checkpoint(self):
#       self._checkpoints[self._timestep] = self._get_checkpoint()

#   def delete_checkpoints(self):
#       self._checkpoints = {}

#   def _get_checkpoint(self):
#       pg = copy.copy(self)
#       pg._checkpoints = {}
#       return pickle.dumps(pg)

#   def _save_actions_for_replay(self, commands, messages):
#       self._actions[self._timestep] = commands, messages


#   def rewind(self, timesteps_rewind, random_alternate: bool = False, **kwargs):

#       # load pg
#       valid_checkpoints = [ts for ts in self._checkpoints.keys()
# if ts <= self._timestep - timesteps_rewind]
#       if not valid_checkpoints:
#           raise ValueError('no checkpoints were saved for rewind')

#       ts_checkpoint = max(valid_checkpoints)
#       pg = pickle.loads(self._checkpoints[ts_checkpoint])

#       # Save before overriding playground
#       future_actions = [self._actions[ts]
# for ts in range(ts_checkpoint, self._timestep-timesteps_rewind)]
#       rng = self._rng
#       checkpoints = self._checkpoints

#       # Time travel
#       self.__dict__.update(pg.__dict__)
#       if random_alternate:
#           self._rng = np.random.default_rng(seed=rng.integers(1000))

#       # Apply all action between checkpoint and rewind point
#       for act in future_actions:
#           self.step(actions=act, compute_observations=False)

#       self._checkpoints = {ts: checkpoint
# for ts, checkpoint in checkpoints.items() if ts <= self._timestep}
#       self._actions = {ts: action
# for ts, action in self._actions.items() if ts <= self._timestep}

#       for view in self._views:
#           view.reset()

#       obs = self._compute_observations(**kwargs)
#       rew = self._compute_rewards(**kwargs)

#       return obs, rew, self.done
