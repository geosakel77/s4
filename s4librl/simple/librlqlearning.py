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

from s4librl.simple.librlbaseagent import BaseAgent
from s4librl.simple.utils import StateEncoderXD
from typing import Dict, Tuple, Any, Optional
from dataclasses import field
import numpy as np

class QLearningAgent(BaseAgent):

    def agent_message(self, message):
        pass

    def agent_cleanup(self):
        pass

    def __init__(self, agent_info):
        super().__init__()
        self.num_actions = None
        self.num_states = None
        self.epsilon = None
        self.step_size = None
        self.discount = None
        self.rand_generator = None
        self.q=None
        self.prev_state = None
        self.prev_action = None
        self.agent_info = agent_info

    def agent_init(self):
        """Setup for the agent called when the experiment first starts.

        Args:
        agent_info (dict), the parameters used to initialize the agent. The dictionary contains:
        {
            num_states (int): The number of states,
            num_actions (int): The number of actions,
            epsilon (float): The epsilon parameter for exploration,
            step_size (float): The step-size,
            discount (float): The discount factor,
        }

        """
        self.num_actions = self.agent_info["num_actions"]
        self.num_states = self.agent_info["num_states"]
        self.epsilon = self.agent_info["epsilon"]
        self.step_size = self.agent_info["step_size"]
        self.discount = self.agent_info["discount"]
        self.rand_generator = np.random.RandomState(self.agent_info["seed"])
        self.q = np.zeros((self.num_states, self.num_actions))

    def agent_start(self, state):
        """The first method called when the episode starts, called after
        the environment starts.
        Args:
            state (int): the state from the
                environment's evn_start function.
        Returns:
            action (int): the first action the agent takes.
        """

        # Choose action using epsilon greedy.
        current_q = self.q[state, :]
        if self.rand_generator.rand() < self.epsilon:
            action = self.rand_generator.randint(self.num_actions)
        else:
            action = self.argmax(current_q)
        self.prev_state = state
        self.prev_action = action
        return action

    def agent_step(self, reward, state):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            state (int): the state from the
                environment's step based on where the agent ended up after the
                last step.
        Returns:
            action (int): the action the agent is taking.
        """
        # Choose action using epsilon greedy.
        current_q = self.q[state, :]
        if self.rand_generator.rand() < self.epsilon:
            action = self.rand_generator.randint(self.num_actions)
        else:
            action = self.argmax(current_q)
        self.q[self.prev_state, self.prev_action] += self.step_size * (
                    reward + self.discount * np.max(current_q) - self.q[self.prev_state, self.prev_action])
        self.prev_state = state
        self.prev_action = action
        return action

    def agent_end(self, reward):
        """Run when the agent terminates.
        Args:
            reward (float): the reward the agent received for entering the
                terminal state.
        """
        self.q[self.prev_state, self.prev_action] += self.step_size * (
                    reward - self.q[self.prev_state, self.prev_action])

    def argmax(self, q_values):
        """argmax with random tie-breaking
        Args:
            q_values (Numpy array): the array of action-values
        Returns:
            action (int): an action with the highest value
        """
        top = float("-inf")
        ties = []

        for i in range(len(q_values)):
            if q_values[i] > top:
                top = q_values[i]
                ties = []

            if q_values[i] == top:
                ties.append(i)

        return self.rand_generator.choice(ties)


class QLearningAgentX(BaseAgent):

    def __init__(self, agent_info):
        super().__init__()
        self.num_actions = None
        self.epsilon = None
        self.alpha = None
        self.gamma = None
        self.agent_info = agent_info
        self.rand_generator = np.random
        self.Q = Dict[Tuple[int, int], float] = field(default_factory=dict)
        self.prev_state = None
        self.prev_action = None


    def _q(self,s:int,a:int) -> float:
        return self.Q.get((s,a),0.0)

    def _best_action(self,s:int) -> int:
        qs = np.array([self._q(s, a) for a in range(self.num_actions)], dtype=float)
        max_q = qs.max()
        best = np.flatnonzero(qs == max_q)
        return int(self.rng.choice(best))

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
        pass

    def agent_step(self, reward, observation):
        pass

    def agent_end(self, reward):
        pass

    def agent_cleanup(self):
        pass

    def agent_message(self, message):
        pass