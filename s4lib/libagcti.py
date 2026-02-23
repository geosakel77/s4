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
from s4lib.libbase import Agent,read_from_json,write_to_json
from s4lib.libdm import Record
from s4lib.apicli.libapiclientagcti import APIClientAgCTI
import random,string,os
import numpy as np
from typing import Dict
from s4librl.librlagent import RLAgent
from s4config.libconstants import RL_FEATURES_DICT_1,RL_FEATURES_DICT_2

def _get_random_key():
    return ''.join(random.choices(string.ascii_lowercase, k=6))

def record_encoder(record:Record,dm_type=0,state_vector_size=49):
    encoded_record=np.zeros(state_vector_size)
    for key in RL_FEATURES_DICT_1.keys():
        if key in record.record_value:
            encoded_record[RL_FEATURES_DICT_1[key]]=1
    for key1 in RL_FEATURES_DICT_2.keys():
        if key1 in record.record_indicator_type:
            encoded_record[RL_FEATURES_DICT_2[key1]+len(RL_FEATURES_DICT_1.keys())]=1
    if record.record_confidence=="low":
        encoded_record[len(RL_FEATURES_DICT_2.keys())+len(RL_FEATURES_DICT_1.keys())]=1
    elif record.record_confidence=="medium":
        encoded_record[len(RL_FEATURES_DICT_2.keys()) + len(RL_FEATURES_DICT_1.keys())+1] = 1
    elif record.record_confidence=="high":
        encoded_record[len(RL_FEATURES_DICT_2.keys()) + len(RL_FEATURES_DICT_1.keys())+2] = 1

    if dm_type==0:
        encoded_record[len(RL_FEATURES_DICT_2.keys()) + len(RL_FEATURES_DICT_1.keys()) + 3] = 1
    elif dm_type==1:
        encoded_record[len(RL_FEATURES_DICT_2.keys()) + len(RL_FEATURES_DICT_1.keys()) + 4] = 1
    elif dm_type==2:
        encoded_record[len(RL_FEATURES_DICT_2.keys()) + len(RL_FEATURES_DICT_1.keys()) + 5] = 1
    return encoded_record

class AgCTI(Agent):
    def __init__(self, agent_uuid, config, agent_type="CTI"):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)
        self.source_score={}
        self.cti_data_current_pool={}
        self.cti_data_received={}
        self.cti_data_send={}
        self.rewards={}
        self.policies:Dict[str, RLAgent] = {}
        self.rl_agent_info=read_from_json(self.config["rl_config_path_simple"])
        self.client=APIClientAgCTI()
        self.source_score_history=[]

    def sends_cti_product(self,src_uuid,product):
        destinations=[]
        for dm_uuid in self.connection_data_dm.keys():
            if self._get_decision(dm_uuid,product):
                destinations.append(dm_uuid)
                self._cti_product_sent(dm_uuid=dm_uuid,src_uuid=src_uuid,product=product)
        self._calculate_source_score()
        return destinations

    def _cti_product_sent(self,dm_uuid,src_uuid,product):
        if src_uuid in self.cti_data_send.keys():
            if dm_uuid in self.cti_data_send[src_uuid].keys():
                self.cti_data_send[src_uuid][dm_uuid].append(product)
            else:
                self.cti_data_send[src_uuid][dm_uuid]=[product]
        else:
            self.cti_data_send[src_uuid]={dm_uuid:[product]}

    def receives_cti_product(self,src_uuid,product):
        if src_uuid in self.cti_data_received.keys():
            self.cti_data_received[src_uuid].append(Record(product['id'],product['type'],product['pattern'],product['confidence'],product['indicator_type']))
            self.cti_data_current_pool[_get_random_key()]={src_uuid:Record(product['id'], product['type'], product['pattern'],product['confidence'],product['indicator_type'])}
        else:
            self.cti_data_received[src_uuid]=[Record(product['id'],product['type'],product['pattern'],product['confidence'],product['indicator_type'])]
            self.cti_data_current_pool[_get_random_key()] = {src_uuid: Record(product['id'], product['type'], product['pattern'],product['confidence'],product['indicator_type'])}
        return {str(self.uuid):f"Product received from {src_uuid}"}

    def _calculate_source_score(self):
        try:
            for src_uuid in self.cti_data_received.keys():
                total=0
                if src_uuid in self.cti_data_send.keys():
                    data_send_from_source=self.cti_data_send[src_uuid]
                    for k,v in data_send_from_source.items():
                        total+=len(v)
                score=total/len(self.cti_data_received[src_uuid])
                print(f"Source score: {score}={total}/{len(self.cti_data_received[src_uuid])} for the {src_uuid}")
                self.source_score[src_uuid]=score
        except Exception as e:
            print(e)
            self.logger.error()


    def get_source_score(self):
        return self.source_score

    def _get_decision(self,dm_uuid,product):
        try:
            if self.connection_data_dm[dm_uuid]['metadata']=="Preventive":
                dm_type=0
            elif self.connection_data_dm[dm_uuid]['metadata']=="Detective":
                dm_type=1
            elif self.connection_data_dm[dm_uuid]['metadata']=="Responsive":
                dm_type=2
            else:
                dm_type=0
            encoded_product=record_encoder(product,dm_type,self.rl_agent_info['state_vector_size'])
            is_created=self.policy_maker(dm_uuid,dm_type)
            if is_created:
                action_decided=self.policies[dm_uuid].agent_start(encoded_record=encoded_product,record_id=product.record_id)
            else:
                action_decided=self.policies[dm_uuid].agent_step(action=0,reward=self.get_last_reward(dm_uuid),encoded_record=encoded_product,record_id=product.record_id)
            if action_decided==0:
                decision=True
            elif action_decided==1:
                decision=False
            else:
                decision=True
        except Exception as e:
            self.logger.error(e)
            decision=True
        return decision

    def set_rewards(self,dm_uuid,reward):
        if dm_uuid in self.rewards.keys():
            self.rewards[dm_uuid].append(reward)
        else:
            self.rewards[dm_uuid]=[reward]
        return {str(self.uuid): f"Reward received {reward}"}

    def get_last_reward(self,dm_uuid):
        last_reward=0
        if dm_uuid in self.rewards.keys():
            last_reward= self.rewards[dm_uuid][-1]
        return last_reward


    def get_cti_product_received(self):
        product_received={}
        for key in self.cti_data_received.keys():
            product_received[key]=len(self.cti_data_received[key])
        return product_received

    def get_total_cti_product_received(self):
        total_cti_product_received=self.get_cti_product_received()
        total_number=0
        for key in total_cti_product_received.keys():
            total_number += total_cti_product_received[key]
        return total_number

    def get_cti_product_send(self):
        product_sent={}
        for key in self.cti_data_send.keys():
            for dm_key in self.cti_data_send[key].keys():
                if dm_key in product_sent.keys():
                    product_sent[dm_key]+=len(self.cti_data_send[key][dm_key])
                else:
                    product_sent[dm_key]=len(self.cti_data_send[key][dm_key])
        return product_sent

    def get_total_cti_product_send(self):
        total_cti_product_send=self.get_cti_product_send()
        total_number=0
        for key in total_cti_product_send.keys():
            total_number += total_cti_product_send[key]
        return total_number

    def get_policies(self):
        policies_status={}
        for key in self.policies.keys():
            policies_status[key]=self.policies[key].get_status()
        return policies_status

    def policy_maker(self,dm_uuid,dm_type):
        is_created=False
        try:
            if dm_uuid not in self.policies.keys():
                self.policies[dm_uuid]=RLAgent(self.config,self.rl_agent_info,dm_uuid,dm_type,self.uuid)
                is_created=True
        except Exception as e:
            self.logger.error(e)
        return is_created

    async def _update_time_actions(self):
        #self.policy_maker()
        product=self._pick_product()
        response_msg = []
        self.store_source_score()
        if product is not None:
            src_uuid,record=next(iter(product.items()))
            destinations=self.sends_cti_product(src_uuid,record)
            for dm_uuid in destinations:
                connection_string= self.connection_data_dm[dm_uuid]
                if connection_string['host'] == "0.0.0.0":
                    dm_url = f"http://127.0.0.1:{connection_string['port']}"
                else:
                    dm_url = f"http://{connection_string['host']}:{connection_string['port']}"
                msg=await self.client.send_cti_product(base_url=dm_url,cti_product={str(dm_uuid):record.serialize()})
                response_msg.append(msg)
        return {self.uuid:response_msg}

    def store_source_score(self):
        self.source_score_history.append(self.get_source_score().copy())
        if self.clock%50==0:
            agent_filename = f"source_score_history_{self.uuid}.json"
            file_path = os.path.join(self.config['experiment_results_path'], agent_filename)
            data={"history":self.source_score_history}
            write_to_json(file_path, data)


    def _pick_product(self):

        product=None
        try:
            if self.cti_data_current_pool:
                k = random.choice(list(self.cti_data_current_pool.keys()))
                product=self.cti_data_current_pool.pop(k)
        except Exception as e:
            self.logger.error(e)
        return product

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'source_score': self.get_source_score(), 'total_received':self.get_total_cti_product_received(),'total_sent':self.get_total_cti_product_send(),
                            'cti_product_received': self.get_cti_product_received(), 'cti_product_send':self.get_cti_product_send(),'policies':self.get_policies()}
        return html_status_data


