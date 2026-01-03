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

from s4lib.libbase import Agent,print_security_characteristics
import random
from s4lib.libia import IA
from s4config.libconstants import IMPACT_LEVELS,CLASSIFICATION_LABELS,PLATFORM_TYPES, DM_TYPES
from typing import Dict,List
import numpy as np
from s4lib.apicli.libapiclientis import APIClientAgIS
from s4lib.libdm import Record

class IS(Agent):

    def __init__(self,agent_uuid,config,agent_type='IS'):
        super().__init__(agent_uuid=agent_uuid,agent_type=agent_type,config=config)
        self.assets:Dict[int,IA]={}
        self.status='normal'
        self.confidentiality_key:int=0
        self.integrity_key:int=0
        self.availability_key:int=0
        self.classification_key:int=0
        self.classification:str=""
        self.confidentiality:str=""
        self.integrity:str=""
        self.availability:str=""
        self.total_value:int=0
        self.client=APIClientAgIS()
        self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                  ("A", self.availability_key))
        self.number_of_assets=random.randint(1,int(self.config['max_number_of_assets']))
        self._create_ia()
        self.determine_security_category()
        self.received_indicators:Dict[str,List:Record]={}
        self.is_compromised_flag=False
        self.platform_type=random.choice(PLATFORM_TYPES)
        self.step_decisions={}

    def handle_indicator_from_ta(self,key,ind):
        value=Record(record_id=ind["id"],record_type=ind["type"],record_value=ind["pattern"])
        if (not value['platform_type']) or (value['platform_type']==self.platform_type):
            if key in self.received_indicators.keys():
                self.received_indicators[key].append(value)
            else:
                self.received_indicators[key]=[value]

    def indicator_detected(self, dm_uuid,decision):
        self.step_decisions[dm_uuid]=decision
        return {dm_uuid:"decision stored"}

    def _step_indicators_decision(self):
        evaluation, status={DM_TYPES[1]:[],DM_TYPES[2]:[],DM_TYPES[3]:[]},"normal"
        for dm_uuid in self.step_decisions.keys():
            decision=self.step_decisions[dm_uuid]
            evaluation[decision["dm_type"]].append(decision["decision"])
        indicators_detection_status={}
        for ta_id,indicators in self.received_indicators.items():
            for indicator in indicators:
                indicator_responses = [False, False, False]
                for decision in evaluation[DM_TYPES[1]]:
                    if indicator.record_id == decision[1]:
                        indicator_responses[0]=decision[0]
                for decision in evaluation[DM_TYPES[2]]:
                    if indicator.record_id == decision[1]:
                        indicator_responses[1]=decision[0]
                for decision in evaluation[DM_TYPES[3]]:
                    if indicator.record_id == decision[1]:
                        indicator_responses[2]=decision[0]
                indicators_detection_status[indicator.record_id]=indicator_responses
        status_array=[]
        for ind in indicators_detection_status.keys():
            if indicators_detection_status[ind][2]:
                status_array.append("normal")
                for ta_id,indicators in self.received_indicators.items():
                    for indicator in indicators:
                        if indicator.record_id == ind:
                            self.received_indicators[ta_id].remove(indicator)
            elif indicators_detection_status[ind][0]:
                status_array.append("normal")
                for ta_id,indicators in self.received_indicators.items():
                    for indicator in indicators:
                        if indicator.record_id == ind:
                            self.received_indicators[ta_id].remove(indicator)
            elif indicators_detection_status[ind][1]:
                status_array.append("compromised")
            else:
                status_array.append("compromised")
        if "compromised" in status_array:
            status="compromised"
        return status

    async def evaluate_indicator(self):
        response_msg=[]
        for dm_uuid in self.connection_data_dm.keys():
            connection_string = self.connection_data_dm[dm_uuid]
            if connection_string['host'] == "0.0.0.0":
                dm_url = f"http://127.0.0.1:{connection_string['port']}"
            else:
                dm_url = f"http://{connection_string['host']}:{connection_string['port']}"
            msg = await self.client.evaluate_indicator(base_url=dm_url,
                                                       indicators={str(self.uuid): self._serialize_received_indicators()})
            response_msg.append(msg)
        return response_msg

    def _serialize_received_indicators(self):
        serialized_received_indicators={}
        for key in self.received_indicators.keys():
            serialized_received_indicators[key]=[]
            for ind in self.received_indicators[key]:
                serialized_received_indicators[key].append(ind.serialize())
        return serialized_received_indicators

    async def _update_time_actions(self):
        response_msg =[]
        msg= await self.evaluate_indicator()
        response_msg.append(msg)
        self.status = self._step_indicators_decision()
        if self.status=="normal" and self.is_compromised_flag:
            self.is_compromised_flag=False
            self.number_of_assets = random.randint(1, int(self.config['max_number_of_assets']))
            self._create_ia()
        if self.status=="compromised":
            self.is_compromised_flag=True
            self.update_ia_status(self.status)
            self.assets = {}
            self.calculate_is_value()
            self.step_decisions={}
        else:
            self.received_indicators = {}
            self.determine_security_category()
            self.calculate_is_value()
            self.update_ia_time(time_step=1)
            self.step_decisions={}
        msg1= await self.send_value_and_state()
        response_msg.append(msg1)
        return {self.uuid: response_msg}

    def _create_ia(self):
        for ia in range(self.number_of_assets):
            self.assets[ia]=IA(self.config)

    def update_ia_time(self,time_step):
        for key,asset in self.assets.items():
            if asset.expired:
                self.assets[key]=IA(self.config)
            else:
                self.assets[key].update_lifespan(time_step)

    def update_ia_status(self,status="normal"):
        for key,asset in self.assets.items():
            self.assets[key].receive_compromised_status(status=status)

    def determine_security_category(self):
        self.classification_key=0
        self.confidentiality_key=0
        self.integrity_key=0
        self.availability_key=0
        for key,asset in self.assets.items():
            if self.confidentiality_key<asset.send_characteristics()[0][0][1]:
                self.confidentiality_key=asset.send_characteristics()[0][0][1]
            if self.integrity_key<asset.send_characteristics()[0][1][1]:
                self.integrity_key=asset.send_characteristics()[0][1][1]
            if self.availability_key<asset.send_characteristics()[0][2][1]:
                self.availability_key=asset.send_characteristics()[0][2][1]
            if self.classification_key<asset.send_characteristics()[1]:
                self.classification_key=asset.send_characteristics()[1]
        self.classification=CLASSIFICATION_LABELS[self.classification_key]
        self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
        self.integrity=IMPACT_LEVELS[self.integrity_key]
        self.availability=IMPACT_LEVELS[self.availability_key]
        self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                  ("A", self.availability_key))

    def calculate_is_value(self):
        if not self.is_compromised_flag:
            self.total_value=0
        for key,asset in self.assets.items():
            value=np.sum([asset.send_characteristics()[0][0][1],asset.send_characteristics()[0][1][1],asset.send_characteristics()[0][2][1]])
            self.total_value+= int(value)*asset.send_characteristics()[1]
        return self.total_value

    def print_is_security_characteristics(self):
        print_security_characteristics(self.security_category,self.confidentiality,self.integrity,self.availability,self.classification,self.classification_key)

    def get_html_status_data(self):
        html_status_data= {'id': self.uuid, 'total_value': self.calculate_is_value(),
                           'security_category': self.security_category, 'confidentiality': self.confidentiality,
                           'integrity': self.integrity, 'availability': self.availability,
                           'classification': self.classification, 'assets': [],'platform_type':self.platform_type}
        for key,asset in self.assets.items():
            html_status_data['assets'].append(asset.get_html_status_data())
        return html_status_data

    async def send_value_and_state(self):
        response_msg = []
        for dm_uuid in self.connection_data_dm.keys():
            connection_string = self.connection_data_dm[dm_uuid]
            if connection_string['host'] == "0.0.0.0":
                dm_url = f"http://127.0.0.1:{connection_string['port']}"
            else:
                dm_url = f"http://{connection_string['host']}:{connection_string['port']}"
            msg = await self.client.send_value_and_state(base_url=dm_url,value_state={str(self.uuid): [self.total_value,self.status,self.security_category,self.classification_key]})
            response_msg.append(msg)
        return response_msg
