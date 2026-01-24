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
from s4lib.libbase import Agent,read_from_json
from s4lib.apicli.libapiclientsrc import APIClientSRC
from s4lib.libdm import Record
from s4config.libconstants import RL_FEATURES_DICT_TO_TYPES
import random

def _set_indicator_types(value):
    if 'indicator_types' in value.keys():
        selected_ind_types=value['indicator_types']
        print(value['indicator_types'])
    else:
        ind_types = []
        for key in RL_FEATURES_DICT_TO_TYPES.keys():
            if key in value['pattern']:
                ind_types.extend(RL_FEATURES_DICT_TO_TYPES[key])
        selected_ind_types = random.sample(list(set(ind_types)), k=random.randint(1, len(set(ind_types))))
    return selected_ind_types

def _set_cti_confidence(value):
    confidence ='low'
    if 'confidence' in value.keys():
        if value['confidence']>=66:
            confidence='high'
        elif value[confidence]>=33 and value['confidence']<66:
            confidence='medium'
        else:
            confidence='low'
    else:
        confidence = random.choice(['low', 'medium', 'high'])
    return confidence


class CTISRC(Agent):
    def __init__(self, agent_uuid, config, agent_type='SRC'):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)
        self.cti_data :dict[int,Record]= self._sample_cti_data()
        self.total_number_of_cti_products=len(self.cti_data.keys())
        self.shared_cti_product =self.cti_data.popitem()[1]
        self.current_number_of_cti_products=len(self.cti_data.keys())
        self.client=APIClientSRC()

    def _sample_cti_data(self):
        cti_data_pool=read_from_json(self.config['cti_data_pool'])
        num_items= random.randint(int(len(cti_data_pool)/3),int(len(cti_data_pool)/2))
        selected_keys=random.sample(list(cti_data_pool.keys()),num_items)
        cti_sample_data ={}
        for key in selected_keys:
            if cti_data_pool[key]['type']=='indicator':
                record_id = cti_data_pool[key]['id']
                record_type = cti_data_pool[key]['type']
                record_confidence = _set_cti_confidence(cti_data_pool[key])
                record_indicator_type=_set_indicator_types(cti_data_pool[key])
                value = cti_data_pool[key]['pattern'].replace("'",'').replace('"','')
                new_record = Record(record_id, record_type, value,record_confidence,record_indicator_type)
                cti_sample_data[key]=new_record
            elif cti_data_pool[key]['type']=='vulnerability':
                record_id = cti_data_pool[key]['id']
                record_type = cti_data_pool[key]['type']
                value = cti_data_pool[key]['name'].replace("'",'').replace('"','')
                record_confidence = _set_cti_confidence(cti_data_pool[key])
                record_indicator_type=_set_indicator_types(cti_data_pool[key])
                new_record = Record(record_id, record_type, value,record_confidence,record_indicator_type)
                cti_sample_data[key]=new_record
        return cti_sample_data

    def sharing_cti_data(self):
        if self.cti_data:
            self.shared_cti_product=self.cti_data.popitem()[1]
        else:
            self.cti_data=self._sample_cti_data()
            self.shared_cti_product=self.cti_data.popitem()[1]
        self.current_number_of_cti_products=len(self.cti_data.keys())

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'shared_cti_product': self.shared_cti_product.serialize(),
                            'total_num_cti': self.total_number_of_cti_products,'current_num_cti': self.current_number_of_cti_products}
        return html_status_data

    async def _update_time_actions(self):
        self.sharing_cti_data()
        for agcti_uuid,connection_string in self.connection_data_cti.items():
            if connection_string['host'] == "0.0.0.0":
                agcti_url = f"http://127.0.0.1:{connection_string['port']}"
            else:
                agcti_url= f"http://{connection_string['host']}:{connection_string['port']}"
            #print(f"Sharing CTI Data with {agcti_uuid} :{agcti_url}")
            await self.client.share_cti_product(base_url=agcti_url,cti_product={str(self.uuid):self.shared_cti_product.serialize()})


if __name__=='__main__':
    from s4config.libconstants import CONFIG_PATH
    from s4config.libconfig import read_config
    config = read_config(CONFIG_PATH)
    ctisrc = CTISRC(agent_uuid='SRC', config=config)
    print(ctisrc.sharing_cti_data())
    print(ctisrc.sharing_cti_data())