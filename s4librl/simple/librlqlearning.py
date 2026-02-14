"""
    Portions of this file are derived from "ChanchalKumarMaji/Reinforcement-Learning-Specialization"
    <https://github.com/ChanchalKumarMaji/Reinforcement-Learning-Specialization/tree/master>

    Original work:
    Copyright (C) 2026  2019 Chanchal Kumar Maji

    Modifications:

    Qualitative Assessment and Application of CTI based on Reinforcement Learning.

    Copyright (C) 2026  Georgios Sakellariou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations
from s4librl.simple.librlbaseagent import BaseAgent
from s4librl.simple.utils import StateEncoderXD
from typing import Dict, Tuple, Any
import numpy as np

class QLearningAgentX(BaseAgent):

    def __init__(self, agent_info):
        super().__init__()
        self.num_actions = None
        self.epsilon = None
        self.alpha = None
        self.gamma = None
        self.agent_info = agent_info
        self.rand_generator = np.random
        self.Q: Dict[Tuple[int, int], float] = {}
        self.prev_state = None
        self.prev_action = None
        self.encoder=StateEncoderXD(x_dimension=self.agent_info["state_vector_size"])
        self.obs_action_dict:Dict[int,int]={}


    def _q(self,s:int,a:int) -> float:
        return self.Q.get((s,a),0.0)

    def _best_action(self,s:int) -> int:
        qs = np.array([self._q(s, a) for a in range(self.num_actions)], dtype=float)
        max_q = qs.max()
        best = np.flatnonzero(qs == max_q)
        return int(self.rand_generator.choice(best))

    def _epsilon_greedy(self,s:int) -> int:
        if self.rand_generator.random() < self.epsilon:
            return int(self.rand_generator.random_integers(0, self.num_actions))
        else:
            return self._best_action(s)

    def agent_init(self):
        """Setup for the agent called when the experiment first starts.

               Args:
               agent_info (dict), the parameters used to initialize the agent. The dictionary contains:
               {
                   num_actions (int): The number of actions,
                   epsilon (float): The epsilon parameter for exploration,
                   alpha (float): The step-size,
                   gamma (float): The discount factor,
                   seed (int): The seed for the random generator
               }

               """
        self.num_actions = self.agent_info["num_actions"]
        self.epsilon = self.agent_info["epsilon"]
        self.alpha = self.agent_info["alpha"]
        self.gamma = self.agent_info["gamma"]
        self.rand_generator.RandomState(self.agent_info["seed"])


    def agent_start(self, observation):
        self.encoder.validate(observation)
        s=self.encoder.encode(observation)
        a = self._epsilon_greedy(s)
        self.prev_state = s
        self.prev_action = a
        self.obs_action_dict[self.prev_state] = self.prev_action
        return a

    def agent_step(self, reward:float, observation:np.ndarray):
        assert self.prev_state is not None and self.prev_action is not None
        s =self.prev_state
        a= self.prev_action
        sp = self.encoder.encode(observation)
        ap=self._epsilon_greedy(sp)

        #Q-learning target (off-policy)
        max_next = max(self._q(sp, a2) for a2 in range(self.num_actions))
        td_target = reward + self.gamma * max_next
        td_error = td_target - self._q(s, a)
        self.Q[(s, a)] = self._q(s, a) + self.alpha * td_error
        self.prev_state = sp
        self.prev_action = ap
        self.obs_action_dict[self.prev_state]=self.prev_action
        return ap

    def agent_end(self, reward):
        assert self.prev_state is not None and self.prev_action is not None
        s = self.prev_state
        a = self.prev_action
        td_target = reward
        td_error = td_target - self._q(s, a)
        self.Q[(s, a)] = self._q(s, a) + self.alpha * td_error
        self.prev_state = None
        self.prev_action = None


    def agent_cleanup(self)->None:
        self.prev_state = None
        self.prev_action = None

    def agent_message(self, message:str)->Any:
        if message == "get_num_q_entries":
            return str(len(self.Q))
        elif message == "get_q":
            return self.Q
        elif message == "get_obs_action":
            return self.obs_action_dict
        else:
            return f"Unknown message:{message}"
