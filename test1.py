import os,json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH


if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    file_paths = os.listdir(config['experiments_data_path'])
    indicators=[]
    for file_path in file_paths:
        with open(os.path.join(".\experiments_data",file_path), 'r',encoding='utf-8') as f:
            data = json.load(f)
            indicators.append(data['indicators'])
    pure_indicators={}
    for indicator in indicators:
        for key in indicator.keys():
            for bundle in indicator[key]:
                if bundle:
                    for ind in bundle['objects']:
                        pure_indicators[ind['id']] = ind
    #print(len(pure_indicators.keys()))
    keys_set=[]
    keys_dict={}
    for key,value in pure_indicators.items():
        keys_set.append(len(value.keys()))
        for key1 in value.keys():
            if key1 in keys_dict.keys():
                keys_dict[key1]+=1
            else:
                keys_dict[key1]=1

    #print(set(keys_set))
    #print(keys_dict)
    #for key,value in keys_dict.items():
    #    print(f"{key}: {value}")
    pattern_types_available=[]
    for key,value in pure_indicators.items():
        if 'pattern' in value.keys():
            v=value['pattern'].split(" ")[0].replace("[","",1).split(".")[0].replace("(","")
            pattern_types_available.append(v)

    print(set(pattern_types_available))
    for pat in set(pattern_types_available):
        print(pat)
    #print(len(set(pattern_types_available)))
    techniques=[]
    for file_path in file_paths:
        with open(os.path.join(".\experiments_data",file_path), 'r',encoding='utf-8') as f:
            data = json.load(f)
            techniques.append(data['techniques'])
    keys_sets_a = []
    keys_dict_a = {}
    platforms=[]
    for technique_list in techniques:
        for technique in technique_list:
            tech_dict=json.loads(technique['object'])
            if 'x_mitre_platforms' in tech_dict.keys():
                platforms.extend(tech_dict['x_mitre_platforms'])
            if 'x_mitre_detection' in tech_dict.keys():
                #print(tech_dict['x_mitre_detection'])
                pass
            keys_sets_a.append(len(tech_dict.keys()))
            for key1 in tech_dict.keys():
                if key1 in keys_dict_a.keys():
                    keys_dict_a[key1] += 1
                else:
                    keys_dict_a[key1] = 1

    #print(set(keys_sets_a))
    #print(keys_dict_a)

    #for key,value in keys_dict_a.items():
    #    print(f"{key}: {value}")

    print(set(platforms))