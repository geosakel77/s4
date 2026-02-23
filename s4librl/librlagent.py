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

from s4config.libconstants import RL_AGENT_TYPES
from s4librl.simple.librlqlearning import QLearningAgentX
from s4librl.simple.librlenvironment import CTIAgentRLEnvironment
from s4librl.simple.librlexpectedsarsa import ExpectedSarsaAgentX
from s4librl.simple.librldiscreteactorcritic import SoftMaxActorCriticX
from s4lib.libbase import write_to_json
import os

class RLAgent:

    def __init__(self,config,agent_info,dm_uuid,dm_type,agcti_uuid):
        self.dm_uuid = dm_uuid
        self.env = CTIAgentRLEnvironment(max_steps=agent_info['max_steps'])
        self.config = config
        self.dm_type = dm_type
        self.agcti_uuid = agcti_uuid

        if config['rl_agent_type']==RL_AGENT_TYPES["QL"]:
            self.algo="QL"
            self.agent = QLearningAgentX(agent_info=agent_info)
        elif config['rl_agent_type']==RL_AGENT_TYPES["ES"]:
            self.algo = "ES"
            self.agent = ExpectedSarsaAgentX(agent_info=agent_info)
        elif config['rl_agent_type']==RL_AGENT_TYPES["DAC"]:
            self.algo = "DAC"
            self.agent = SoftMaxActorCriticX(agent_info=agent_info)
        else:
            self.algo = "QL"
            self.agent = QLearningAgentX(agent_info=agent_info)
        self.returns = []
        self.decisions={}
        self.goal=0.0
        self.terminal=False
        self.agent.agent_init()
        self.num_episodes=self.config["rl_num_episodes"]

    def get_returned_actions(self):
        return self.returns

    def agent_start(self,encoded_record,record_id):
        observation=self.env.env_start(encoded_record)
        action=self.agent.agent_start(observation)
        self.decisions[record_id]=action
        return action

    def agent_step(self,action,reward,encoded_record,record_id):
        decided_action=0
        if self.num_episodes>0:
            if not self.terminal:
                r, obs2,terminal=self.env.env_step(action,reward,encoded_record)
                self.goal+=r
                self.terminal=terminal
                if self.terminal:
                    self.agent.agent_end(r)
                    self.agent.agent_cleanup()
                    self.env.env_cleanup()
                    self.num_episodes-=1
                    self.returns.append(self.goal)
                else:
                    decided_action=self.agent.agent_step(r,obs2)
                    self.decisions[record_id]=decided_action
            elif self.terminal:
                decided_action=self.agent_start(encoded_record,record_id)
                self.terminal=False
        elif self.num_episodes==0:
            agent_filename=f"{self.agcti_uuid}_{self.dm_uuid}_{self.dm_type}_agent_{self.algo}.json"
            file_path=os.path.join(self.config['experiment_results_path'],agent_filename)
            experiment_results=self.get_status()
            write_to_json(file_path,experiment_results)
            self.num_episodes=-1
        return decided_action

    def get_status(self):
        if self.algo == "DAC":
            experiment_results = {"dm_uuid": self.dm_uuid, "dm_type": self.dm_type, "algo": self.algo,
                                  "decided_actions": self.decisions, "episode_goals": self.returns,
                                  "num_q_entries": self.agent.agent_message('get_shapes'),
                                  'w_pi': self.agent.agent_message('get_w_pi'),
                                  'obs_actions': self.agent.agent_message('get_obs_action')}
        else:
            experiment_results = {"dm_uuid": self.dm_uuid, "dm_type": self.dm_type, "algo": self.algo,
                                  "decided_actions": self.decisions, "episode_goals": self.returns,
                                  "num_q_entries": self.agent.agent_message('get_num_q_entries'),
                                  'q': self.agent.agent_message('get_q'),
                                  'obs_actions': self.agent.agent_message('get_obs_action')}
        return experiment_results







