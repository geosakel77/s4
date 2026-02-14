from s4librl.simple.librlbaseenvironment import BaseEnvironment
from s4config.libconstants import RL_FEATURES_DICT_1, RL_FEATURES_DICT_2
import numpy as np

class CTIAgentRLEnvironment(BaseEnvironment):
    def __init__(self,max_steps=100):
        super().__init__()
        self.current_state = None
        self.state = None
        self.states_counter=len(RL_FEATURES_DICT_1.keys())+len(RL_FEATURES_DICT_2.keys())+3+3
        self.count=0
        self.max_steps=100



    def env_init(self, env_info=None):
        self.state = np.zeros(self.states_counter)

    def env_start(self, env_info=None):
        self.current_state = env_info

    def env_step(self, action, reward, env_info=None):
        if self.max_steps>0:
            terminal=False
        else:
            terminal=True
        self.reward_obs_term = (reward,env_info,terminal)
        self.max_steps-=1
        return self.reward_obs_term

    def env_cleanup(self):
        pass

    def env_message(self, message):
        pass

