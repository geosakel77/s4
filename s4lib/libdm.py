from s4lib.libbase import  Agent
from dataclasses import dataclass
from typing import List, Tuple, Dict
import random
from s4config.libconstants import DM_TYPES,IND_TYPES

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
        return answer

    def update_knowledge_base(self,record: Record):
        if record.record_id not in self.knowledge_base.keys():
            self.knowledge_base_values.append(record.record_value)
            self.knowledge_base[record.record_id] = record
        else:
            print("Record value already exists in knowledge_base")


class DM(Agent):
    def __init__(self,dm_agent_uuid,dm_type,dm_config,dm_agent_type="DM"):
        super().__init__(agent_uuid=dm_agent_uuid,agent_type=dm_agent_type,config=dm_config)
        self.dm_type=dm_type
        self.engine=Engine()
        self.step_indicators=[]
        self.indicator_types=IND_TYPES[dm_type]
        self.check_cti_product_applicability=True
        self.hit_status=False
        self.reg_is={}

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

    def _register_is(self,is_uuid,value,state,security_category,classification):
        self.reg_is[is_uuid]=[value,state,security_category,classification]


    def get_html_status_data(self):
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

    def handle_indicator_from_ta(self,indicator):
        self.indicator_types.append({'ta':indicator})


class PreventionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[1],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)
        self.hardened_is={}

    def _handle_indicator_from_is(self,is_uuid,indicator):
        self.step_indicators.append({'is':indicator})
        compromised_status=True
        if any(ind_type in indicator.record_type for ind_type in self.indicator_types) or any(ind_type in indicator.record_value for ind_type in self.indicator_types):
            if any(ind_type in indicator.record_value for ind_type in [self.indicator_types[2],self.indicator_types[3]]):
                if is_uuid in self.hardened_is.keys():
                    self.hit_status=True
                    compromised_status=False
                else:
                    self.hit_status=self.engine.reasoning(indicator)
                    if self.hit_status:
                        compromised_status=False
                    else:
                        compromised_status=True
        return compromised_status

    def harden_is(self):
        if self.config['hardening_threshold']>random.random():
            sampled_is= random.sample(list(self.reg_is.keys()),random.randint(0,len(list(self.reg_is.keys()))-1))
            for is_key in sampled_is:
                self.hardened_is[is_key]=self.clock+self.config['harden_q_steps']

    def _update_time_actions(self):
        for is_key in self.hardened_is.keys():
            if self.hardened_is[is_key]-1>0:
                self.hardened_is[is_key]=self.hardened_is[is_key]-1
            else:
                self.hardened_is.pop(is_key)
        reward=self.rewards_cti_agent()
        self.check_cti_product_applicability=False
        self.hit_status=False
        self.step_indicators=[]
        return reward

class DetectionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[2],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)

    def _handle_indicator_from_is(self,is_uuid,indicator):
        self.step_indicators.append({'is': indicator})
        compromised_status = True
        if any(ind_type in indicator.record_value for ind_type in self.indicator_types):
            self.hit_status = self.engine.reasoning(indicator)
            if self.hit_status:
                compromised_status = False
            else:
                compromised_status = True
        return compromised_status

    def _update_time_actions(self):
        reward = self.rewards_cti_agent()
        self.check_cti_product_applicability = False
        self.hit_status = False
        self.step_indicators = []
        return reward

class ResponseDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[3],dm_agent_type="DM"):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config,dm_agent_type=dm_agent_type)

    def _handle_indicator_from_is(self,is_uuid,indicator):
        self.step_indicators.append({'is': indicator})
        compromised_status = True
        if any(ind_type in indicator.record_value for ind_type in self.indicator_types):
            self.hit_status = self.engine.reasoning(indicator)
            if self.hit_status:
                compromised_status = False
            else:
                compromised_status = True
        return compromised_status

    def _update_time_actions(self):
        reward = self.rewards_cti_agent()
        self.check_cti_product_applicability = False
        self.hit_status = False
        self.step_indicators = []
        return reward