from openpyxl.styles.builtins import total

from s4lib.libbase import Agent,print_security_characteristics
import random
from s4lib.libia import IA
from s4config.libconstants import IMPACT_LEVELS,CLASSIFICATION_LABELS
from typing import Dict
import numpy as np



class IS(Agent):

    def __init__(self,agent_uuid,config,agent_type='IS'):
        super().__init__(agent_uuid=agent_uuid,agent_type=agent_type,config=config)
        self.assets:Dict[int,IA]={}
        self.confidentiality_key:int=0
        self.integrity_key:int=0
        self.availability_key:int=0
        self.classification_key:int=0
        self.classification:str=""
        self.confidentiality:str=""
        self.integrity:str=""
        self.availability:str=""
        self.total_value:int=0
        self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                  ("A", self.availability_key))
        self.number_of_assets=random.randint(1,int(config['max_number_of_assets']))
        self._create_ia()
        self.determine_security_category()

    def _update_time_actions(self):
        self.update_ia_time(time_step=1)
        self.determine_security_category()
        self.calculate_is_value()

    def _create_ia(self):
        for i in range(self.number_of_assets):
            self.assets[i]=IA(self.config)

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
                           'classification': self.classification, 'assets': []}
        for key,asset in self.assets.items():
            html_status_data['assets'].append(asset.get_html_status_data())
        return html_status_data


if __name__=="__main__":
    import uuid
    from s4config.libconfig import read_config
    from s4config.libconstants import CONFIG_PATH
    config_data = read_config(CONFIG_PATH)
    is_agent=IS(str(uuid.uuid4()),config_data,agent_type="IS")
    for i in range(0,10000):
        is_agent.update_ia_time(time_step=1)
        is_agent.determine_security_category()
        is_agent.calculate_is_value()
        if i%200==0:
            is_agent.print_is_security_characteristics()
            print(f"IS Value:{is_agent.total_value}")
