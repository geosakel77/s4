from s4lib.libbase import read_from_json
from s4config.libconstants import DM_TYPES
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve,roc_auc_score,precision_recall_curve,average_precision_score
from s4statistics.libstatistics import prepare_agents_data


def get_exp_details(exp_path):
    exp_files = [f for f in os.listdir(str(exp_path)) if "agent" in f]
    source_score_files = [os.path.join(str(exp_path), f) for f in os.listdir(str(exp_path)) if "source_score" in f]
    agent_ids=[source_score_file.split("_")[4].split(".")[0] for source_score_file in source_score_files]
    details={}
    for agent_id in agent_ids:
        for exp_file in exp_files:
            if agent_id in exp_file:
                details[agent_id]=exp_file.split("_")[4].split(".")[0]
    return details

def prepare_source_score_data(config,exp):
    exp_path=os.path.join(config['experiment_results_path'],exp)
    source_score_files=[os.path.join(str(exp_path),f) for f in os.listdir(str(exp_path)) if "source_score" in f]

    exp_details=get_exp_details(exp_path)
    records = []
    for source_score_file in source_score_files:
        agent_cti_id=source_score_file.split("_")[4].split(".")[0]
        score_data=read_from_json(source_score_file)["history"]
        sources_keys = {}
        k = 0
        for source in score_data[-1].keys():
            sources_keys[k] = source
            k += 1
        time = 1
        for measurement in score_data:
            record = {
                "agent_id": agent_cti_id,
                'time': time,
                "algo":exp_details[agent_cti_id]}
            for key, item in sources_keys.items():
                record[f"src_{key}"] = measurement.get(item, 0)
            time += 1
            records.append(record)
    df = pd.DataFrame(records)
    print(df.head())
    df.to_csv(os.path.join(config['experiment_results_path'],"source_score",f"{exp}_source_score.csv"),index=False)


def prepare_agent_data(config,exp):
    exp_path=os.path.join(config['experiment_results_path'],exp)
    exp_details=get_exp_details(exp_path)
    data_decided_actions=[]
    data_episode_goals=[]
    path_a={"experiment_results_path":exp_path}
    agents_data=prepare_agents_data(path_a)
    for agent_id,value in agents_data.items():
        for dm in value:
            for indicator,decision in dm["decided_actions"].items():
                row_decided_actions = {"agent_id": agent_id, "algo": exp_details[agent_id], "dm_uuid": dm["dm_uuid"],
                   "dm_type": DM_TYPES[dm["dm_type"] + 1],"indicator": indicator, "decision": decision}
                data_decided_actions.append(row_decided_actions)
            episode=0
            cumulative_goal=0
            for goal in dm["episode_goals"]:
                cumulative_goal+=goal
                row_episode_goals={"agent_id": agent_id, "algo": exp_details[agent_id], "dm_uuid": dm["dm_uuid"],
             "dm_type": DM_TYPES[dm["dm_type"] + 1],"episode": episode, "goal": goal,"cumulative_goal":cumulative_goal}
                data_episode_goals.append(row_episode_goals)

    df_decided_actions = pd.DataFrame(data_decided_actions)
    df_episode_goals = pd.DataFrame(data_episode_goals)
    print(df_decided_actions.head())
    print(df_episode_goals.head())
    df_decided_actions.to_csv(os.path.join(config['experiment_results_path'], "agents_data", f"{exp}_decided_actions.csv"), index=False)
    df_episode_goals.to_csv(os.path.join(config['experiment_results_path'], "agents_data", f"{exp}_episode_goals.csv"), index=False)




