from s4lib.libbase import AttackerAgent,read_from_json,write_to_json,OpenAIClient
from config.libconstants import MAP_TECHNIQUES_TO_TACTICS
from pprint import pprint
import random,os,json,re,time




class TA(AttackerAgent):

    def __init__(self,agent_type="TA",actor_name=None):
        super().__init__(agent_type=agent_type)
        actors = read_from_json(self.config['actors_path'])
        if actor_name is None:
            self.actor_id=random.choice(list(actors.keys()))
            self.actor_name=actors[self.actor_id]
        else:
            for key,value in actors.items():
                if value['name'] == actor_name:
                    self.actor_id=key
            self.actor_name=actor_name
        self.actor_conf_file=f"{self.actor_id}.json"

        if os.path.exists(os.path.join(self.config['experiments_data_path'],self.actor_conf_file)):
            actors_config=read_from_json(os.path.join(self.config['experiments_data_path'],self.actor_conf_file))
            self.actor=actors_config['actor']
            self.actor_techniques=actors_config['techniques']
            self.actor_software=actors_config['software']
            self.actor_techniques_software_map=actors_config['actor_techniques_software_map']
            self.actor_techniques_to_tactics_map=actors_config['actor_techniques_to_tactics_map']
            self.indicators=actors_config['indicators']
        else:
            actors_config={}
            self.actor = actors[self.actor_id]
            techniques_used_by_groups=read_from_json(self.config['techniques_used_by_groups'])
            if self.actor_id in techniques_used_by_groups.keys():
                self.actor_techniques=techniques_used_by_groups[self.actor_id]
            else:
                self.actor_techniques=[]
            software_used_by_groups=read_from_json(self.config['software_used_by_groups'])
            if self.actor_id in software_used_by_groups.keys():
                self.actor_software=software_used_by_groups[self.actor_id]
            else:
                self.actor_software=[]
            if self.actor_techniques and self.actor_software:
                self.actor_techniques_software_map\
                    =self._map_actor_techniques_to_software()
            else:
                self.actor_techniques_software_map={}
            if self.actor_techniques:
                self.actor_techniques_to_tactics_map=self._map_actor_techniques_to_tactics()
            else:
                self.actor_techniques_to_tactics_map={}
            self.indicators = self._generate_indicators()
            actors_config['actor']=self.actor
            actors_config['techniques']=self.actor_techniques
            actors_config['software']=self.actor_software
            actors_config['actor_techniques_software_map']=self.actor_techniques_software_map
            actors_config['actor_techniques_to_tactics_map']=self.actor_techniques_to_tactics_map
            actors_config['indicators']=self.indicators
            write_to_json(os.path.join(self.config['experiments_data_path'],self.actor_conf_file),actors_config)





    def _map_actor_techniques_to_software(self):
            actor_techniques_map={}
            actor_techniques_ids=[]
            actor_software_ids=[]
            for technique in self.actor_techniques:
               actor_techniques_ids.append(json.loads(technique['object'])['id'])
            for software in self.actor_software:
                actor_software_ids.append(json.loads(software['object'])['id'])
            software_using_technique=read_from_json(self.config['software_using_technique'])
            for technique_id in actor_techniques_ids:
                map=[]
                if technique_id in software_using_technique.keys():
                    software_obj_list = software_using_technique[technique_id]
                    for software_obj in software_obj_list:
                        software_id= json.loads(software_obj['object'])['id']
                        if software_id in actor_software_ids:
                            map.append(software_id)
                actor_techniques_map[technique_id] = map
            return actor_techniques_map

    def _map_actor_techniques_to_tactics(self):
        actor_techniques_to_tactics_map={}
        map_techniques_to_tactics= MAP_TECHNIQUES_TO_TACTICS
        for tactic in map_techniques_to_tactics.keys():
            list_of_techniques = []
            for technique in self.actor_techniques:
                technique_deserialized = json.loads(technique['object'])
                technique_external_id=technique_deserialized['external_references'][0]['external_id']
                if technique_deserialized['x_mitre_is_subtechnique']:
                    check_data= technique_external_id.split('.')[0]
                else:
                    check_data= technique_external_id
                if check_data in map_techniques_to_tactics[tactic]:
                    list_of_techniques.append(technique_deserialized['id'])
            if len(list_of_techniques)>0:
                actor_techniques_to_tactics_map[tactic] = list_of_techniques
        return actor_techniques_to_tactics_map






if __name__ == "__main__":

    for i in range(1,100):
        ta=TA()
        time.sleep(random.randint(30,60))
        print(ta.actor_name)





