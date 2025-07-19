from lib.libbase import Agent,read_from_json
from pyattck import Attck
import random


class TA(Agent):

    def __init__(self,agent_type="TA",actor_name=None):
        super().__init__(agent_type=agent_type)
        self.mitre_attack=Attck(nested_techniques=True,use_config=True,
                                config_file_path=self.config['pyattck_path'],
                                data_path=self.config['pyattck_data'],
                                enterprise_attck_json=self.config['enterprise_attck_path'],
                                generated_nist_json=self.config['generated_nist_path'],
                                ics_attck_json=self.config['ics_attck_path'],
                                mobile_attck_json=self.config['mobile_attck_path'],
                                nist_controls_json=self.config['nist_controls_path'],
                                pre_attck_json=self.config['pre_attck_path'])
        if actor_name is None:
            actors=read_from_json(self.config['actors_path'])
            self.actor_name= actors[random.choice(list(actors.keys()))]
        else:
            self.actor_name=actor_name
        self.actor = self._get_actor(self.actor_name)



    def _get_actor(self,actor_name):
        result=None
        for actor in self.mitre_attack.enterprise.actors:
            if actor.name == actor_name:
                result=actor
        return result

    def get_techniques(self):
        techniques=self.actor.techniques
        for technique in techniques:
            print(technique)


    def get_external_references(self):
        external_references=self.actor.external_references
        for external_reference in external_references:
            print(external_reference)
        return external_references







if __name__ == "__main__":
    ta =TA(actor_name="APT29")
    print(ta.agent_type)
    ta.get_external_references()