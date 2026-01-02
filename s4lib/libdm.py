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
from s4lib.libbase import  Agent
from dataclasses import dataclass
from typing import List, Tuple, Dict
import random
from s4config.libconstants import DM_TYPES,IND_TYPES
from s4lib.apicli.libapiclientdm import APIClientAgDM,APIClientAgDetectionDM

@dataclass(slots=True)
class Record:
    record_id : str
    record_type : str
    record_value : str

    def serialize(self):
        return {
            "id":self.record_id,
            "type":self.record_type,
            "pattern":self.record_value,
        }


class Engine:
    def __init__(self):
        self.knowledge_base: Dict[str, Record] = {}
        self.knowledge_base_values: List[Record.record_value] = []

    def reasoning(self,indicator : Record):
        if indicator.record_id in self.knowledge_base.keys():
            answer=True
        else:
            if any(indicator.record_value in value for value in self.knowledge_base_values):
                answer=True
            else:
                answer=False
        return answer,indicator.record_id

    def update_knowledge_base(self,record: Record):
        if record.record_id not in self.knowledge_base.keys():
            self.knowledge_base_values.append(record.record_value)
            self.knowledge_base[record.record_id] = record
        else:
            print("Record value already exists in knowledge_base")

    def get_knowledge_base(self):
        serialized_knowledge_base = {}
        for key, value in self.knowledge_base.items():
            serialized_knowledge_base[key]=value.serialize()
        return serialized_knowledge_base


class DM(Agent):
    def __init__(self,dm_agent_uuid,dm_type,dm_config,dm_agent_type="DM"):
        super().__init__(agent_uuid=dm_agent_uuid,agent_type=dm_agent_type,config=dm_config)
        self.dm_type=dm_type
        self.engine=Engine()
        self.step_indicators=[]
        self.indicator_types=IND_TYPES[dm_type]
        self.check_cti_product_applicability=True
        self.hit_status=False
        self.step_hit_status=[]
        self.reg_is={}
        self.client=APIClientAgDM()



    def rewards_cti_agent(self):
        r_is=0
        h_r=0
        a_r=0
        for is_uuid, is_tuple in self.reg_is.items():
            if is_tuple[1]=='normal':
                v1=1
            else:
                v1=-1
            v2=is_tuple[2][0][1]*is_tuple[2][1][1] *is_tuple[2][2][1] *is_tuple[3]
            r_is=r_is+v1*v2*is_tuple[0]
        if self.hit_status:
            h_r=self.config['hit_reward']
        if self.check_cti_product_applicability:
            a_r=self.config['applicability_reward']
        reward=h_r*self.config['l1']+ a_r*self.config['l2']+ r_is*self.config['l3']
        return {str(self.uuid):reward}

    async def send_reward(self,reward):
        print(f"Sending reward  {reward}")
        response_msg = []
        for agcti_uuid,connection_string in self.connection_data_cti.items():
            if connection_string['host'] == "0.0.0.0":
                agcti_url = f"http://127.0.0.1:{connection_string['port']}"
            else:
                agcti_url= f"http://{connection_string['host']}:{connection_string['port']}"
            msg=await self.client.rewards_cti_agent(base_url=agcti_url,reward=reward)
            response_msg.append(msg)
        return {self.uuid:response_msg}

    def _register_is(self,is_uuid,value,state,security_category,classification):
        self.reg_is[is_uuid]=[value,state,security_category,classification]

    def receives_value_and_state(self,is_uuid,value_state):
        self._register_is(is_uuid,value=value_state[0],state=value_state[1],security_category=value_state[2],classification=value_state[3])

    def get_indicator_types(self):
        return self.indicator_types

    def get_html_status_data(self):
        pass

    def _handle_indicator_from_is(self,is_uuid,indicator: Record):
        pass

    def handle_indicator_from_agcti(self, indicator: Record):
        self.step_indicators.append({'agcti':indicator})
        if indicator.record_type in self.indicator_types:
            self.check_cti_product_applicability = True
            self.engine.update_knowledge_base(indicator)
        else:
            for ind_type in self.indicator_types:
                if ind_type in indicator.record_value:
                    self.check_cti_product_applicability = True
                    self.engine.update_knowledge_base(indicator)
                    break
        return {str(self.uuid):f"Indicator received from AgCTI"}

    def handle_indicator_from_ta(self,indicator):
        self.indicator_types.append({'ta':indicator})

    async def detect_indicator(self, is_uuid, decision):
        connection_string = self.connection_data_is[is_uuid]
        if connection_string['host'] == "0.0.0.0":
            is_url = f"http://127.0.0.1:{connection_string['port']}"
        else:
            is_url = f"http://{connection_string['host']}:{connection_string['port']}"
        msg = await self.client.detect_indicator(base_url=is_url,decision={str(self.uuid):{"decision":decision,"dm_type":self.dm_type}})
        return msg

class PreventionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[1],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)
        self.hardened_is={}

    async def _handle_indicator_from_is(self,is_uuid,indicators):
        received_indicators = []
        for key in indicators.keys():
            for ind in indicators[key]:
                received_indicators.append(Record(record_id=ind["id"],record_type=ind["type"],record_value=ind["pattern"]))
        self.step_indicators.append({is_uuid: received_indicators})
        check_result=[]
        for indicator in received_indicators:
            check_result.append(self._models_vulnerability(is_uuid,indicator)[is_uuid])
        self.step_hit_status.extend(check_result)
        msg = await self.detect_indicator(is_uuid, check_result)
        return msg


    def _models_vulnerability(self,is_uuid,indicator:Record):
        hit_status=False
        indicator_id = indicator.record_id
        if any(ind_type in indicator.record_type for ind_type in self.indicator_types) or any(
                ind_type in indicator.record_value for ind_type in self.indicator_types):
            if any(ind_type in indicator.record_value for ind_type in
                   [self.indicator_types[2], self.indicator_types[3]]):
                if is_uuid in self.hardened_is.keys():
                    hit_status = True
                else:
                    hit_status,indicator_id = self.engine.reasoning(indicator)
        decision = {is_uuid: (hit_status,indicator_id)}
        return decision

    def harden_is(self):
        for is_key in self.hardened_is.keys():
            if self.hardened_is[is_key] - 1 > 0:
                self.hardened_is[is_key] = self.hardened_is[is_key] - 1
            else:
                self.hardened_is.pop(is_key)
        if self.config['hardening_threshold']>random.random():
            sampled_is= random.sample(list(self.reg_is.keys()),random.randint(0,len(list(self.reg_is.keys()))-1))
            for is_key in sampled_is:
                self.hardened_is[is_key]=self.clock+self.config['harden_q_steps']

    async def _update_time_actions(self):
        step_status=[]
        for decision in self.step_hit_status:
            step_status.append(decision[0])
        if True in step_status:
            self.hit_status=True
        else:
            self.hit_status=False
        reward=self.rewards_cti_agent()
        self.check_cti_product_applicability=False
        self.hit_status=False
        self.step_hit_status=[]
        self.step_indicators=[]
        response= await self.send_reward(reward)
        self.harden_is()
        return response

    def get_hardened_is(self):
        return self.hardened_is

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'dm_type':self.dm_type,'hardened_is': self.get_hardened_is(),
                            'indicator_types': self.get_indicator_types(),
                            'knowledge_base': self.engine.get_knowledge_base()}
        print(html_status_data)
        return html_status_data

class DetectionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[2],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)
        self.detections={}

    async def _handle_indicator_from_is(self,is_uuid,indicators):
        received_indicators = []
        for key in indicators.keys():
            for ind in indicators[key]:
                received_indicators.append(
                    Record(record_id=ind["id"], record_type=ind["type"], record_value=ind["pattern"]))
        self.step_indicators.append({is_uuid: received_indicators})
        check_result=[]
        for indicator in received_indicators:
            check_result.append(self._check_detection(is_uuid,indicator)[is_uuid])
        self.step_hit_status.extend(check_result)
        msg = await self.detect_indicator(is_uuid, check_result)
        return msg

    def _check_detection(self,is_uuid,indicator:Record):
        hit_status=False
        indicator_id = indicator.record_id
        if any(ind_type in indicator.record_value for ind_type in self.indicator_types):
            hit_status,indicator_id = self.engine.reasoning(indicator)
            if hit_status:
                self.detections[is_uuid] = {"indicator": indicator.serialize(), "timestamp": self.clock}
        decision = {is_uuid: (hit_status,indicator_id)}
        return decision

    def get_detections(self):
        return self.detections

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'dm_type':self.dm_type,'detections': self.get_detections(),
                            'indicator_types': self.get_indicator_types(),
                            'knowledge_base': self.engine.get_knowledge_base()}
        return html_status_data

    async def _update_time_actions(self):
        step_status = []
        for decision in self.step_hit_status:
            step_status.append(decision[0])
        if True in step_status:
            self.hit_status = True
        else:
            self.hit_status = False
        reward = self.rewards_cti_agent()
        self.check_cti_product_applicability = False
        self.hit_status = False
        self.step_hit_status=[]
        self.step_indicators = []
        response = await self.send_reward(reward)
        return response


class ResponseDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[3],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)
        self.responses={}


    async def _handle_indicator_from_is(self,is_uuid,indicators):
        received_indicators = []
        for key in indicators.keys():
            for ind in indicators[key]:
                received_indicators.append(
                    Record(record_id=ind["id"], record_type=ind["type"], record_value=ind["pattern"]))
        self.step_indicators.append({is_uuid: received_indicators})
        check_result = []
        for indicator in received_indicators:
            check_result.append(self._evict_isolate(is_uuid, indicator)[is_uuid])
        self.step_hit_status.extend(check_result)
        msg = await self.detect_indicator(is_uuid, check_result)
        return msg


    def _evict_isolate(self, is_uuid,indicator:Record):
        hit_status = False
        indicator_id = indicator.record_id
        if any(ind_type in indicator.record_value for ind_type in self.indicator_types):
            hit_status,indicator_id = self.engine.reasoning(indicator)
            if hit_status:
                self.responses[is_uuid] = {"indicator": indicator.serialize(), "timestamp": self.clock}
        decision = {is_uuid: (hit_status,indicator_id)}
        return decision

    def get_responses(self):
        return self.responses

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'dm_type': self.dm_type, 'responses': self.get_responses(),
                            'indicator_types': self.get_indicator_types(),
                            'knowledge_base': self.engine.get_knowledge_base()}
        return html_status_data

    async def _update_time_actions(self):
        step_status = []
        for decision in self.step_hit_status:
            step_status.append(decision[0])
        if True in step_status:
            self.hit_status = True
        else:
            self.hit_status = False
        reward = self.rewards_cti_agent()
        self.check_cti_product_applicability = False
        self.hit_status = False
        self.step_indicators = []
        response = await self.send_reward(reward)
        return response