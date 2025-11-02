import os.path,pprint
from pickle import FALSE
from s4config.libconfig import read_config
from s4lib.libbase import read_from_json
from mitreattack.stix20 import MitreAttackData
from stix2 import FileSystemStore
from typing import List
import json,re,tempfile


if __name__=="__main__":
    check_url="https://securelist.com/el-machete/66108/"
    config_file = '../s4config/config.ini'
    config = read_config(config_file)
    actors = read_from_json(config['actors_path'])
    for actor_key in actors.keys():
        actor = actors[actor_key]
        for external_reference in actor['external_references']:
            if external_reference['url']==check_url:
                print(f"{actor['id']} actor has the article {check_url}")
        actor_software=[]
        software_used_by_groups = read_from_json(config['software_used_by_groups'])
        if actor['id'] in software_used_by_groups.keys():
            actor_software = software_used_by_groups[actor['id']]
        for software in actor_software:
            software_json=json.loads(software['object'])
            for json_ref in software_json['external_references']:
                if "url" in json_ref.keys():
                    if json_ref['url']==check_url:
                        print(f"{actor['id']} has the software {software_json['id']} with the article {check_url}")