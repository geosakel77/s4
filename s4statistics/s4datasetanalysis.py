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

import os,json
from s4config.libconfig import read_config
from s4lib.libbase import read_from_json
from s4config.libconstants import CONFIG_PATH
from matplotlib import pyplot as plt

def get_actors_statistics(actors_path,verbose_flag=False):
    with open(actors_path, 'r', encoding='utf-8') as f:
        actors = json.load(f)
    if verbose_flag:
        print("MITRE ATT&CK Threat Actors Available for the Experiments")
        print("TA ID - Name")
        for key, item in actors.items():
            print(f"{key}: {item['name']}")
    print(f"Total number of Threat Actor in MITRE ATT&CK {len(actors.keys())}")

def get_ta_data_statistics(experiments_data_path,verbose_flag=False):
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
    stats_indicator_per_pattern_type = {}
    for key, value in indicator_per_pattern_type.items():
        stats_indicator_per_pattern_type[key] = len(set(value))
    ta_platforms={}
    ta_techniques_lists={}
    for ta_key,technique_list in techniques.items():
        platforms = []
        ta_techniques_lists[ta_key]=[]
        for technique in technique_list:
            tech_dict = json.loads(technique['object'])
            ta_techniques_lists[ta_key].append(tech_dict)
            if 'x_mitre_platforms' in tech_dict.keys():
                platforms.extend(tech_dict['x_mitre_platforms'])
        ta_platforms[ta_key]=platforms

    total_indicators = 0
    total_number_of_patterns = []
    total_number_of_techniques = []
    total_number_of_platforms = []
    print('MITRE ATT&CK Threat Actors Utilized for the Experiments with their Characteristics')
    print("TA Name - Number of Indicators - Number of Techniques - Number of Available Patterns - Number of Applicable Platforms")
    for key in pure_indicators.keys():

        print(f"{actors[key]} : {len(pure_indicators[key])} - {len(ta_techniques_lists[key])} - {len(set(pattern_types_available[key]))} - {len(set(ta_platforms[key]))}")
        total_indicators += len(pure_indicators[key])
        total_number_of_patterns.extend(pattern_types_available[key])
        total_number_of_techniques.extend([ technique['id'] for technique in ta_techniques_lists[key]])
        total_number_of_platforms.extend(ta_platforms[key])

    print(f"Total Number of of Actors in TAs Repository: {len(pure_indicators.keys())}")
    print(f"Total number of Indicators in TAs Repository: {total_indicators}")
    print(f"Total Number of Patterns in TAs Repository: {len(set(total_number_of_patterns))}")
    print(f"Total Number of Techniques in TAs Repository: {len(set(total_number_of_techniques))}")
    print(f"Total Number of Platforms in TAs Repository: {len(set(total_number_of_platforms))}")
    if verbose_flag:
        print("Distribution of Indicators in TA Repository per Pattern Type")
        print("Pattern Type  - Number of Indicators")
        for key, value in stats_indicator_per_pattern_type.items():
            print(f"{key} - {value}")
    return stats_indicator_per_pattern_type

def get_src_data_statistics(cti_data_pool_path,verbose_flag=False):
    cti_data_pool = read_from_json(cti_data_pool_path)
    print('CTI Sources Statistics Utilized for the Experiments with their Characteristics')
    pure_indicators = []
    pattern_types_available = []
    indicator_per_pattern_type = {}
    for key, indicator in cti_data_pool.items():
        pure_indicators.append(indicator['id'])
        if 'pattern' in indicator.keys():
            v = indicator['pattern'].split(" ")[0].replace("[", "", 1).split(".")[0].replace("(", "")
            if len(v) > 3:
                pattern_types_available.append(v)
                if v in indicator_per_pattern_type.keys():
                    indicator_per_pattern_type[v].append(indicator['id'])
                else:
                    indicator_per_pattern_type[v]=[indicator['id']]
    stats_indicator_per_pattern_type = {}
    for key, value in indicator_per_pattern_type.items():
        stats_indicator_per_pattern_type[key] = len(set(value))
    print(f"Total number of Indicators in CTI Pool Repository: {len(set(pure_indicators))}")
    print(f"Total Number of Patterns in CTI Pool Repository: {len(set(pattern_types_available))}")
    if verbose_flag:
        print("Distribution of Indicators in CTI Pool Repository per Pattern Type")
        print("Pattern Type  - Number of Indicators")
        for key, value in stats_indicator_per_pattern_type.items():
            print(f"{key} : {value}")
    return stats_indicator_per_pattern_type

def plot_bar_data_statistics(name,config_data,data):
    filename=os.path.join(config_data["images_path"],"bar_"+name)
    top5 = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
    labels = [k for k, _ in top5]
    values = [v for _, v in top5]
    # Plot
    plt.figure()
    plt.bar(labels, values)
    plt.title("Top 5 Patterns")
    plt.xlabel("Pattern")
    plt.ylabel("Indicators")
    plt.xticks(rotation=45, ha="right")
    plt.savefig(filename)
    plt.tight_layout()
    plt.show()

def plot_pie_data_statistics(name,config_data,data,title):
    filename=os.path.join(config_data["images_path"],"pie_"+name)
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    # Top 5
    top5 = sorted_items[:5]
    top5_labels = [k for k, _ in top5]
    top5_values = [v for _, v in top5]
    # Others
    others_value = sum(v for _, v in sorted_items[5:])
    labels = top5_labels + ["Others"]
    values = top5_values + [others_value]
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(aspect="equal"))
    wedges, texts, autotexts = ax.pie(
        values,
        autopct='%1.1f%%',
        startangle=140
    )
    ax.legend(
        handles=wedges,
        labels=labels,
        title="Observable Patterns",
        loc='center left',
        bbox_to_anchor=(1,0,0.5,1)
    )
    plt.setp(texts, size=8, weight='bold')
    ax.set_title(f"{title} Indicators Distribution over Patterns")
    #plt.xticks(rotation=45, ha="right")
    plt.savefig(filename)
    plt.tight_layout()
    plt.show()

def generate_statistics(config_data,verbose_flag=False,plot=False):
    print("Generating statistics of the dataset utilized during the experiments of S4...\n")
    print("-------------------------------------------------------------------------------")
    get_actors_statistics(config_data["actors_path"],verbose_flag)
    print("-------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------")
    ta_stat_data=get_ta_data_statistics(config_data['experiments_data_path'],verbose_flag)
    print("-------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------")
    src_stat_data=get_src_data_statistics(config_data['cti_data_pool'])
    if plot:
        plot_bar_data_statistics("ta_patterns_data.png",config_data,ta_stat_data)
        plot_bar_data_statistics("src_patterns_data.png",config_data,src_stat_data)
        plot_pie_data_statistics("ta_patterns_data.png", config_data, ta_stat_data, "CTI SRC")
        plot_pie_data_statistics("src_patterns_data.png", config_data, src_stat_data, "TA")

    print("-------------------------------------------------------------------------------")

if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    generate_statistics(config,True)
