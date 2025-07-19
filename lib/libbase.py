import json
from config.libconfig import read_config
from pyattck import Attck

def write_to_json(json_file,json_data):
    with open(json_file,'w') as outfile:
        json.dump(json_data,outfile)

def read_from_json(json_file):
    with open(json_file,'r') as infile:
        json_data = json.load(infile)
        return json_data

class Agent:
    def __init__(self,agent_type,config_file='C:\\Users\\geosa\\PycharmProjects\\s4\\config\\config.ini'):
        self.agent_type=agent_type
        self.config=read_config(config_file)


class MITREATTCKConfig(Agent):

    def __init__(self,agent_type="MITREATTCK"):
        super().__init__(agent_type=agent_type)
        self.mitre_attack = Attck(nested_techniques=True, use_config=True,
                                  config_file_path=self.config['pyattck_path'],
                                  data_path=self.config['pyattck_data'],
                                  enterprise_attck_json=self.config['enterprise_attck_path'],
                                  generated_nist_json=self.config['generated_nist_path'],
                                  ics_attck_json=self.config['ics_attck_path'],
                                  mobile_attck_json=self.config['mobile_attck_path'],
                                  nist_controls_json=self.config['nist_controls_path'],
                                  pre_attck_json=self.config['pre_attck_path'])
        self.actors= self._get_actors()

    def _get_actors(self):
        actors ={}
        for actor in self.mitre_attack.enterprise.actors:
            actors[actor.id]=actor.name
        return actors