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

import json,random
from s4config.libconstants import CONFIG_PATH,RL_FEATURES_DICT_TO_TYPES
from s4config.libconfig import read_config
from s4lib.libbase import read_from_json

def cti_data_pool_analysis(config_dic):
    data = read_from_json(config_dic["cti_data_pool"])
    no_pattern=[]
    with_pattern=[]
    indicator_keys=[]
    text=""
    confidence_index=[]
    pulsedive_risk=[]
    indicator_types=[]
    for key,value in data.items():
        if "pattern" in value.keys():
            indicator_keys.extend(list(value.keys()))
            if 'confidence' in value.keys():
                confidence_index.append(value['confidence'])
            if 'pulsedive_risk' in value.keys():
                pulsedive_risk.append(value['pulsedive_risk'])
            if 'indicator_types' in value.keys():
                indicator_types.extend(value['indicator_types'])
            text=text+json.dumps(value)+"\n"
            with_pattern.append(value['pattern'].split(" ")[0].replace("[", "", 1).split(".")[0].replace("(", ""))
        else:
            no_pattern.append(key)
    actual_features_1=[]
    for value in set(with_pattern):
        if len(value)>2:
            if 'import' not in value.lower():
                actual_features_1.append(value)
    features_1_dict={}
    index=0
    for feature in actual_features_1:
        features_1_dict[feature]=index
        index+=1
    features_2_dict = {}
    index = 0
    for feature in set(indicator_types):
        features_2_dict[feature] = index
        index += 1
    print(features_1_dict)
    print(features_2_dict)

    return features_1_dict,features_2_dict

def cti_data_pool_analysis2(config_dic):
    data = read_from_json(config_dic["cti_data_pool"])
    confidence_index = []
    indicator_types = []
    check=[]
    for key, value in data.items():
        if "pattern" in value.keys():
            if 'confidence' in value.keys():
                confidence_index.append(value['confidence'])
                print(f"{value['confidence']} - {value['pattern']}")
            else:
                confidence=random.choice(['low', 'medium', 'high'])
                print(f"{confidence} - {value['pattern']}")
            if 'indicator_types' in value.keys():
                indicator_types.append(len(value['indicator_types']))
                print(value['indicator_types'])
            else:
                ind_types = []
                for key in RL_FEATURES_DICT_TO_TYPES.keys():
                    if key in value['pattern']:
                        ind_types.extend(RL_FEATURES_DICT_TO_TYPES[key])
                selected_ind_types=random.sample(list(set(ind_types)),k=random.randint(1,len(set(ind_types))))
                print(selected_ind_types)
                if ind_types:
                    indicator_types.append(ind_types)
                else:
                    check.append(["not found"])
    print(check)

if __name__=="__main__":
    config = read_config(CONFIG_PATH)
    cti_data_pool_analysis(config)
    #cti_data_pool_analysis2(config)