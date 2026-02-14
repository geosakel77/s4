"""
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

from s4librl.simple.librlenvironment import CTIAgentRLEnvironment
from s4librl.simple.librlqlearning import QLearningAgent
from s4librl.utils import CTIAgentRLObservationsGenerator,CTIAgentRewardsGenerator
from s4librl.simple.utils import StateEncoderXD

def run_environment_test():
    cti_agent_environment = CTIAgentRLEnvironment()
    reward_generator = CTIAgentRewardsGenerator(timesteps=100)
    state_observation_generator = CTIAgentRLObservationsGenerator()
    cti_agent_environment.env_start(state_observation_generator.generate_state_observation())
    agent_info={"num_actions":2}

def run_reward_generator_test():
    reward_generator = CTIAgentRewardsGenerator(timesteps=100)
    for i in range(100):
        print(f"Reward produced: {reward_generator.next_step()}")

def run_state_observation_generator_test():
    state_observation_generator= CTIAgentRLObservationsGenerator()
    for i in range(5):
        print(state_observation_generator.generate_state_observation())

def run_state_discretizer_test():
    state_observation_generator = CTIAgentRLObservationsGenerator()
    state_encoder = StateEncoderXD()
    for i in range(5):
        state=state_observation_generator.generate_state_observation()
        print(state)
        print(state_encoder.encode(state))

if __name__ == '__main__':
    #run_environment_test()
    #run_reward_generator_test()
    #run_state_observation_generator_test()
    run_state_discretizer_test()
