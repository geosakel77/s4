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
from s4lib.libbase import AttackerAgent,read_from_json,write_to_json
from s4lib.apicli.libapiclientta import APIClientAgTA
from s4lib.libdm import Record
from s4config.libconstants import MAP_TECHNIQUES_TO_TACTICS, EXPERIMENTS_ACTORS
import random,os,json

class TA(AttackerAgent):

    def __init__(self,ta_agent_uuid,ta_config,agent_type="TA",actor_name=None):
        super().__init__(agent_uuid=ta_agent_uuid,agent_type=agent_type,config=ta_config)
        self.ta_plan_threshold=float(self.config['ta_plan_threshold'])
        self.plan=None
        self.plan_indicators=None
        self.ta_actor_max_plans=int(self.config['ta_actor_max_plans'])
        self.all_techniques=read_from_json(self.config['techniques_path'])
        if actor_name is None:
            actor_name=random.choice(EXPERIMENTS_ACTORS)
        self._initiate(actor_name=actor_name)
        self.create_plan()
        self.client=APIClientAgTA()


    def _initiate(self,actor_name=None):
        actors = read_from_json(self.config['actors_path'])
        if actor_name is None:
            self.actor_id=random.choice(list(actors.keys()))
            self.actor_name=actors[self.actor_id]["name"]
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
                map_i=[]
                if technique_id in software_using_technique.keys():
                    software_obj_list = software_using_technique[technique_id]
                    for software_obj in software_obj_list:
                        software_id= json.loads(software_obj['object'])['id']
                        if software_id in actor_software_ids:
                            map_i.append(software_id)
                actor_techniques_map[technique_id] = map_i
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

    def create_plan(self):
        plan={}
        plan_indicators={}
        for tactic in self.actor_techniques_to_tactics_map.keys():
            ta_e = random.random()
            if ta_e>self.ta_plan_threshold:
                k =random.randint(1,len(self.actor_techniques_to_tactics_map[tactic]))
                plan_techniques_of_tactic_n=random.sample(self.actor_techniques_to_tactics_map[tactic],k)
                plan_soft_tools_of_tactic_n = {}
                if self.actor_techniques_software_map:
                    for technique in plan_techniques_of_tactic_n:
                        l = random.randint(0,len(self.actor_techniques_software_map[technique]))
                        sample_tools=random.sample(self.actor_techniques_software_map[technique],l)
                        if len(sample_tools)>0:
                            plan_soft_tools_of_tactic_n[technique]=sample_tools
                plan[tactic]=(plan_techniques_of_tactic_n,plan_soft_tools_of_tactic_n)
        indicators = []
        if self.indicators:
            for ref in self.indicators[self.actor_id]:
                if ref:
                    for obj in ref['objects']:
                        if 'pattern' in obj.keys():
                            indicators.append({obj["id"]:obj['pattern']})

        for tactic_n in plan.keys():
            plan_indicators[tactic_n]=[]
            if len(indicators)>0:
                m=random.randint(0,len(indicators))
                indexes = sorted(random.sample(range(len(indicators)), m), reverse=True)
                plan_indicators[tactic_n].extend([indicators.pop(i) for i in indexes])
            for technique, tool in plan[tactic_n][1].items():
                for tl in tool:
                    bundles=self.indicators[tl]
                    for bundle in bundles:
                        plan_indicators[tactic_n].extend([{indicator['id']:indicator['pattern']} for indicator in bundle['objects'] if 'pattern' in indicator.keys()])
        self.plan=plan
        self.plan_indicators=plan_indicators
        if (not self.plan) and indicators:
            #Special case that handles threat actors with no identified techniques or tactics which have indicators.
            plan_indicators["T000N"]=[]
            plan["T000N"]=(["TE000N"],{"TE000N":["TO000N"]})
            m = random.randint(0, len(indicators))
            indexes = sorted(random.sample(range(len(indicators)), m), reverse=True)
            plan_indicators["T000N"].extend([indicators.pop(i) for i in indexes])
        return plan,plan_indicators

    def action_attack(self):
        flag=True
        selected_indicator=None
        while flag:
            if len(self.plan_indicators)>0:
                tactic, indicators= next(iter(self.plan_indicators.items()))
                if indicators:
                    selected_indicator=indicators.pop()
                    flag=False
                else:
                    self.plan_indicators.pop(tactic)
            else:
                flag=False

        return selected_indicator

    async def _execute_attack_step_is(self,is_uuid,selected_indicator:Record):
        connection_string = self.connection_data_is[is_uuid]
        if connection_string['host'] == "0.0.0.0":
            is_url = f"http://127.0.0.1:{connection_string['port']}"
        else:
            is_url = f"http://{connection_string['host']}:{connection_string['port']}"
        msg = await self.client.execute_attack_step(base_url=is_url,indicator={str(self.uuid):selected_indicator.serialize()})
        return msg

    async def _execute_attack_step_dm(self,dm_uuid,selected_indicator:Record):
        connection_string = self.connection_data_dm[dm_uuid]
        if connection_string['host'] == "0.0.0.0":
            dm_url = f"http://127.0.0.1:{connection_string['port']}"
        else:
            dm_url = f"http://{connection_string['host']}:{connection_string['port']}"
        msg = await self.client.execute_attack_step(base_url=dm_url,indicator={str(self.uuid):selected_indicator.serialize()})
        return msg

    def get_html_status_data(self):
        translated_plan={}
        for key1 in self.plan.keys():
            translated_phase=[]
            phase=self.plan[key1][0]
            soft_of_phase=self.plan[key1][1]
            for atptn in phase:
                if atptn in self.all_techniques.keys():
                    translated_phase.append((self.all_techniques[atptn]['technique_id'],self.all_techniques[atptn]['name']))
                else:
                    translated_phase.append((atptn,atptn))
            translated_soft={}
            for key2 in soft_of_phase.keys():
                if key2 in self.all_techniques.keys():
                    translated_soft[self.all_techniques[key2]['technique_id']]=soft_of_phase[key2]
                else:
                    translated_soft[key2]=soft_of_phase[key2]
            translated_plan[key1]=(translated_phase,translated_soft)


        html_status_data= {'id': self.actor_id, 'name': self.actor_name, 'plan': translated_plan,
                           'plan_indicators': self.plan_indicators}

        return html_status_data

    def _update_time_actions(self):
        selected_indicator=self.action_attack()
        if selected_indicator is None:
            if self.ta_actor_max_plans>0:
                self.create_plan()
                self.ta_actor_max_plans-=1
                selected_indicator=self.action_attack()
            else:
                self.plan = None
                self.plan_indicators = None
                self.ta_actor_max_plans = int(self.config['ta_actor_max_plans'])
                actor_name = random.choice(EXPERIMENTS_ACTORS)
                self._initiate(actor_name=actor_name)
                self.create_plan()
        else:
            pass

        return selected_indicator

if __name__ == "__main__":
    import uuid,pprint
    from s4config.libconfig import read_config
    from s4config.libconstants import CONFIG_PATH
    config =read_config(CONFIG_PATH)
    agent_uuid = uuid.uuid4()
    ta_name="GALLIUM"#"Dragonfly 2.0"#None#"APT34"#'ZIRCONIUM'
    ta=TA(ta_agent_uuid=agent_uuid,ta_config=config,agent_type="TA",actor_name=ta_name)
    print(ta.actor_name)




