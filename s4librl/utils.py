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
from s4config.libconstants import RL_FEATURES_DICT_1, RL_FEATURES_DICT_2,DM_TYPES,TYPES_OF_DATA,CLASSIFICATION_LABELS,IMPACT_LEVELS
from s4config.libconstants import CONFIG_PATH
from s4lib.libia import IA
import numpy as np
from s4config.libconfig import read_config
import random

class CTIAgentRLObservationsGenerator:
    def __init__(self):
        self.state_observation=np.zeros(len(RL_FEATURES_DICT_1.keys())+len(RL_FEATURES_DICT_2.keys())+3+3)


    def generate_state_observation(self):
        """Configure the IoCs part of the observation."""
        sample = random.sample(list(RL_FEATURES_DICT_1.keys()), random.randint(1, len(RL_FEATURES_DICT_1.keys())))

        for t in sample:
            self.state_observation[RL_FEATURES_DICT_1[t]]=1

        """Configure the IoC types part of the observation."""
        sample1 = random.sample(list(RL_FEATURES_DICT_2.keys()), random.randint(1, len(RL_FEATURES_DICT_2.keys())))

        for k in sample1:
            self.state_observation[RL_FEATURES_DICT_2[k]+len(RL_FEATURES_DICT_1.keys())]=1
        """Configure the Confidence part of the observation."""
        confidence_choices=[0,1,2]
        conf_index=random.choice(confidence_choices)+len(RL_FEATURES_DICT_1.keys())+len(RL_FEATURES_DICT_2.keys())
        self.state_observation[conf_index]=1
        """Configure the DM type part of the observation."""
        dm_type_choices=[0,1,2]
        dm_type_index=random.choice(dm_type_choices)+len(RL_FEATURES_DICT_1.keys())+len(RL_FEATURES_DICT_2.keys())+len(confidence_choices)
        self.state_observation[dm_type_index]=1
        state_observation=self.state_observation
        self._reset_state_observation()
        return state_observation

    def _reset_state_observation(self):
        self.state_observation = np.zeros(len(RL_FEATURES_DICT_1.keys()) + len(RL_FEATURES_DICT_2.keys()) + 3 + 3)

class CTIAgentRewardsGenerator:
    def __init__(self,timesteps=100,number_of_assets=3,number_of_is=2):
        self.config= read_config(CONFIG_PATH)
        self.config['time_steps']=timesteps
        self.config['max_number_of_assets']=number_of_assets
        self.information_systems=[]
        for i in range(number_of_is):
            assets=[]
            for k in range(number_of_assets):
                assets.append(IA(self.config))
            self.information_systems.append(self.InfSystem(self.config,assets))

    def next_step(self):
        hit_status=random.choice([True, False])
        check_cti_product_applicability = random.choice([True, False])
        reward =self._generate_reward(hit_status,check_cti_product_applicability)
        for information_system in self.information_systems:
            if random.random() < 0.1:
                status = "compromised"
            else:
                status = "normal"
            self.information_systems[self.information_systems.index(information_system)].update_on_step(status)
        return reward

    def _generate_reward(self,hit_status,check_cti_product_applicability):
        r_is = 0
        h_r = 0
        a_r = 0
        for  information_system in self.information_systems:
            is_tuple = information_system.get_value_and_state()
            if is_tuple[1] == 'normal':
                v1 = 1
            else:
                v1 = -1
            v2 = is_tuple[2][0][1] * is_tuple[2][1][1] * is_tuple[2][2][1] * is_tuple[3]
            r_is = r_is + v1 * v2 * is_tuple[0]
        if hit_status:
            h_r = self.config['hit_reward']
        if check_cti_product_applicability:
            a_r = self.config['applicability_reward']
        reward = h_r * self.config['l1'] + a_r * self.config['l2'] + r_is * self.config['l3']
        return reward

    class InfSystem:
        def __init__(self,config,assigned_assets):
            self.config = config
            self.assigned_assets = assigned_assets
            self.is_compromised_flag=False
            self.status = 'normal'
            self.confidentiality_key: int = 0
            self.integrity_key: int = 0
            self.availability_key: int = 0
            self.classification_key: int = 0
            self.classification: str = ""
            self.confidentiality: str = ""
            self.integrity: str = ""
            self.availability: str = ""
            self.total_value: int = 0
            self.security_category=None
            self.determine_security_category()

        def update_on_step(self,status="normal",):
            if self.status == "normal" and self.is_compromised_flag:
                self.is_compromised_flag = False
                number_of_assets = random.randint(1, int(self.config['max_number_of_assets']))
                assets=[]
                for k in range(number_of_assets):
                    assets.append(IA(self.config))
                self.assigned_assets=assets
            if self.status == "compromised":
                self.is_compromised_flag = True
                self.update_ia_status(self.status)
                self.assigned_assets=[]
                self.calculate_is_value()
            else:
                self.determine_security_category()
                self.calculate_is_value()
                self.update_ia_time(time_step=1)

        def get_value_and_state(self):
            return [self.total_value,self.status,self.security_category,self.classification_key]

        def set_compromised(self,status):
            self.is_compromised_flag=status

        def calculate_is_value(self):
            if not self.is_compromised_flag:
                self.total_value = 0
            for asset in self.assigned_assets:
                value = np.sum([asset.send_characteristics()[0][0][1], asset.send_characteristics()[0][1][1],
                                asset.send_characteristics()[0][2][1]])
                self.total_value += int(value) * asset.send_characteristics()[1]
            return self.total_value

        def determine_security_category(self):
            self.classification_key = 0
            self.confidentiality_key = 0
            self.integrity_key = 0
            self.availability_key = 0
            for asset in self.assigned_assets:
                if self.confidentiality_key < asset.send_characteristics()[0][0][1]:
                    self.confidentiality_key = asset.send_characteristics()[0][0][1]
                if self.integrity_key < asset.send_characteristics()[0][1][1]:
                    self.integrity_key = asset.send_characteristics()[0][1][1]
                if self.availability_key < asset.send_characteristics()[0][2][1]:
                    self.availability_key = asset.send_characteristics()[0][2][1]
                if self.classification_key < asset.send_characteristics()[1]:
                    self.classification_key = asset.send_characteristics()[1]
            self.classification = CLASSIFICATION_LABELS[self.classification_key]
            self.confidentiality = IMPACT_LEVELS[self.confidentiality_key]
            self.integrity = IMPACT_LEVELS[self.integrity_key]
            self.availability = IMPACT_LEVELS[self.availability_key]
            self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                      ("A", self.availability_key))

        def update_ia_time(self, time_step):
            for asset in self.assigned_assets:
                if asset.expired:
                    self.assigned_assets.remove(asset)
                    self.assigned_assets.append(IA(self.config))
                else:
                    self.assigned_assets[self.assigned_assets.index(asset)].update_lifespan(time_step)

        def update_ia_status(self, status="normal"):
            for asset in self.assigned_assets:
                    self.assigned_assets[self.assigned_assets.index(asset)].receive_compromised_status(status=status)