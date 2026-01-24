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


"""
An abstract class that specifies the Agent API for RL CTI agent.
"""

from abc import ABCMeta, abstractmethod

class BaseAgent(metaclass=ABCMeta):
    """Implements the RL agent for AgCTI.
    Note:
        agent_init, agent_start, agent_step, agent_end, agent_cleanup, and
        agent_message are required methods.
    """


    def __init__(self):
        pass

    @abstractmethod
    def agent_init(self):
        """Setup for the agent called when the AgCTI  first starts."""

    @abstractmethod
    def agent_start(self, observation):
        """The first method called when the experiment starts, called after
        the environment starts.
        Args:
            observation (Numpy array): the state observation from the environment's evn_start function.
        Returns:
            The first action the agent takes.
        """

    @abstractmethod
    def agent_step(self, reward, observation):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            observation (Numpy array): the state observation from the
                environment's step based, where the agent ended up after the
                last step
        Returns:
            The action the agent is taking.
        """

    @abstractmethod
    def agent_end(self, reward):
        """Run when the agent terminates.
        Args:
            reward (float): the reward the agent received for entering the terminal state.
        """

    @abstractmethod
    def agent_cleanup(self):
        """Cleanup done after the agent ends."""

    @abstractmethod
    def agent_message(self, message):
        """A function used to pass information from the RL agent to the AgCTI.
        Args:
            message: The message passed to the agent.
        Returns:
            The response (or answer) to the message.
        """