import os,json
from s4lib.libbase import read_from_json
from s4config.libconstants import MAP_TECHNIQUES_TO_TACTICS, EXPERIMENTS_ACTORS
import pandas as pd
from s4lib.libbase import read_from_json
from s4lib.libsrc import _set_cti_confidence,_set_indicator_types
from s4lib.libdm import Record


def get_pattern_types(experiments_data_path):
    file_paths = os.listdir(experiments_data_path)
    indicators={}
    actors={}
    techniques = {}
    for file_path in file_paths:
        with open(os.path.join(experiments_data_path, file_path), 'r', encoding='utf-8') as f:
            data = json.load(f)
            indicators[data['actor']['id']]=data['indicators']
            actors[data['actor']['id']]=data['actor']['name']
            techniques[data['actor']['id']]=data['techniques']
    pure_indicators = {}
    pattern_types_available = {}
    indicator_per_pattern_type = {}
    for ta_key, ta_indicators in indicators.items():
        pure_indicators[ta_key] = []
        pattern_types_available[ta_key] = []
        for bundle_key in ta_indicators.keys():
            for bundle in ta_indicators[bundle_key]:
                if bundle:
                    for indicator in bundle['objects']:
                        pure_indicators[ta_key].append(indicator)
                        if 'pattern' in indicator.keys():
                            v = indicator['pattern'].split(" ")[0].replace("[", "", 1).split(".")[0].replace("(", "")
                            if len(v)>3:
                                pattern_types_available[ta_key].append(v)
                                if v in indicator_per_pattern_type.keys():
                                    indicator_per_pattern_type[v].append(indicator['id'])
                                else:
                                    indicator_per_pattern_type[v] = [indicator['id']]
    return list(indicator_per_pattern_type.keys())

class TADatasetCreator:

    def __init__(self,ta_config):
        self.config = ta_config
        self.plan=None
        self.plan_indicators=None
        self.all_techniques=read_from_json(self.config['techniques_path'])
        self.actor_names=EXPERIMENTS_ACTORS
        self.pattern_types=get_pattern_types(self.config['experiments_data_path'])
        self.ta_dataset_df=self.create_all_plans()

    def get_dataset(self):
        return self.ta_dataset_df

    def create_all_plans(self):
        ta_dataset=[]
        for actor_name in self.actor_names:
            actor_id=self._initiate(actor_name=actor_name)
            plan,plan_indicators=self.create_plan()
            for key, value in plan_indicators.items():
                for indicator in value:
                    for ind_id,body in indicator.items():
                        pattern_type=None
                        for pt in self.pattern_types:
                            if pt in body['pattern']:
                                pattern_type=pt
                                break
                        for platform in body['platform']:
                            row={
                                "actor_id":actor_id,
                                "actor_name":actor_name,
                                'tactic':key,
                                "indicator_id":ind_id,
                                "pattern_type":pattern_type,
                                "pattern":body['pattern'],
                                "platform":platform,
                            }
                            ta_dataset.append(row)
        ta_dataset_df=pd.DataFrame(ta_dataset)
        return ta_dataset_df

    def _initiate(self,actor_name):
        actors = read_from_json(self.config['actors_path'])
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
            print("Error: Actor not found")
        return self.actor_id

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
            plan_techniques_of_tactic_n=self.actor_techniques_to_tactics_map[tactic]
            plan_soft_tools_of_tactic_n = {}
            if self.actor_techniques_software_map:
                for technique in plan_techniques_of_tactic_n:
                    sample_tools=self.actor_techniques_software_map[technique]
                    if len(sample_tools)>0:
                        plan_soft_tools_of_tactic_n[technique]=sample_tools
            plan[tactic]=(plan_techniques_of_tactic_n,plan_soft_tools_of_tactic_n)
        indicators = []
        if self.indicators:
            for ref in self.indicators[self.actor_id]:
                if ref:
                    for obj in ref['objects']:
                        if 'pattern' in obj.keys():
                            indicators.append({obj["id"]:{"pattern":obj['pattern'],"platform":["generic"]}})

        for tactic_n in plan.keys():
            plan_indicators[tactic_n]=[]
            if len(indicators)>0:
                indexes = sorted(range(len(indicators)), reverse=True)
                plan_indicators[tactic_n].extend([indicators.pop(i) for i in indexes])
            for technique, tool in plan[tactic_n][1].items():
                for tl in tool:
                    bundles=self.indicators[tl]
                    for bundle in bundles:
                        platform=[]
                        for obj in self.actor_techniques:
                            data = json.loads(obj['object'])
                            if technique == data['id']:
                                platform.extend(data['x_mitre_platforms'])
                        plan_indicators[tactic_n].extend([{indicator['id']:{"pattern":indicator['pattern'],"platform":platform}} for indicator in bundle['objects'] if 'pattern' in indicator.keys()])
        self.plan=plan
        self.plan_indicators=plan_indicators
        if (not self.plan) and indicators:
            #Special case that handles threat actors with no identified techniques or tactics which have indicators.
            plan_indicators["T000N"]=[]
            plan["T000N"]=(["TE000N"],{"TE000N":["TO000N"]})
            indexes = sorted(range(len(indicators)), reverse=True)
            plan_indicators["T000N"].extend([indicators.pop(i) for i in indexes])
        return plan,plan_indicators

class CTIPoolDatasetCreator:
    def __init__(self, config):
        self.config=config
        self.cti_data :dict[int,Record]= self._sample_cti_data()
        self.pattern_types = get_pattern_types(self.config['experiments_data_path'])
        self.cti_pool_dataset_df=self.create_cti_pool_dataset_df()

    def get_cti_pool_dataset_df(self):
        return self.cti_pool_dataset_df

    def _sample_cti_data(self):
        cti_sample_data = {}
        try:
            cti_data_pool=read_from_json(self.config['cti_data_pool'])
            selected_keys=list(cti_data_pool.keys())
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
        except Exception as e:
            print(e)
        return cti_sample_data

    def create_cti_pool_dataset_df(self):
        all_cti_data=[]
        for key, value in self.cti_data.items():
            for indicator_type in value.record_indicator_type:
                pattern_type=None
                for pt in self.pattern_types:
                    if pt in value.record_value:
                        pattern_type=pt
                row={"ind_id":value.record_id,
                     "type":value.record_type,
                    "pattern":value.record_value,
                     "confidence":value.record_confidence,
                     "indicator_type":indicator_type,
                     "pattern_type":pattern_type}
                all_cti_data.append(row)
        return pd.DataFrame(all_cti_data)