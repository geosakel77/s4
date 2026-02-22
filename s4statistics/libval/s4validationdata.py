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

from s4config.libconfig import read_config
from s4lib.libbase import read_from_json,write_to_json
from s4config.libconstants import CONFIG_PATH,RL_FEATURES_DICT_1,RL_FEATURES_DICT_2,RL_FEATURES_DICT_TO_TYPES,IND_TYPES
import os

def generate_validation_data(config_data):
    cti_data_pool = read_from_json(config_data['cti_data_pool'])
    print(len(set(list(cti_data_pool.keys()))))
    cti_data_pool_decisions={}
    for key, item in cti_data_pool.items():
        item_decision={0:1,1:1,2:1,"id":item["id"]}
        if "pattern" in item.keys():
            for pattern in IND_TYPES['Preventive']:
                if pattern in item["pattern"]:
                    item_decision[0]=0
            for pattern in IND_TYPES['Detective']:
                if pattern in item["pattern"]:
                    item_decision[1]=0
            for pattern in IND_TYPES['Responsive']:
                if pattern in item["pattern"]:
                    item_decision[2]=0
        elif "type" in item.keys():
            for pattern in IND_TYPES['Preventive']:
                if pattern in item["type"]:
                    item_decision[0]=0
            for pattern in IND_TYPES['Detective']:
                if pattern in item["type"]:
                    item_decision[1]=0
            for pattern in IND_TYPES['Responsive']:
                if pattern in item["type"]:
                    item_decision[2]=0
        else:
            print(item)
        cti_data_pool_decisions[key]=item_decision
    return cti_data_pool_decisions

def validation_data_statistics(validation_data):
    print("Validation Data Statistics")
    print(f"Validation Data Items {len(validation_data.keys())}")
    counter0=0
    counter1=0
    counter2=0
    for key, item in validation_data.items():
        counter0+=item[0]
        counter1+=item[1]
        counter2+=item[2]
    validation_statistics=(f"Preventive DMs: {len(validation_data.keys())-counter0}\n"
                           f"Detective DMs: {len(validation_data.keys())-counter1}\n"
                           f"Responsive DMs: {len(validation_data.keys())-counter2}\n")
    print(validation_statistics)

def run():
    config = read_config(CONFIG_PATH)
    validation_data=generate_validation_data(config)
    validation_data_statistics(validation_data)
    validation_data_filename=os.path.join(config["validation_data_dir"],"validation_data.json")
    write_to_json(validation_data_filename,validation_data)

if __name__=="__main__":
    run()