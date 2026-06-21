import pandas as pd
import numpy as np
import os
from datetime import datetime
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
import uuid
from s4lib.libbase import read_from_json

def load_data(config):
    exp0_filename = os.path.join(config['experiment_results_path'], "agents_data", f"exp0_decided_actions.csv")
    exp0_df = pd.read_csv(exp0_filename)
    return exp0_df

def random_selection(df):
    random_uuid = "random_"+str(uuid.uuid4())
    new_df = df.copy()
    uuid_map = {
        old_id: random_uuid
        for old_id in new_df["agent_id"].unique()
    }

    new_df["agent_id"] = new_df["agent_id"].map(uuid_map)

    # Random decisions (50% probability)
    new_df["decision"] = np.random.randint(0, 2, size=len(new_df))
    return new_df

def heuristic_selection(df):
    heur_uuid = "heuristic_"+str(uuid.uuid4())
    new_df = df.copy()
    uuid_map = {
        old_id: heur_uuid
        for old_id in new_df["agent_id"].unique()
    }

    new_df["agent_id"] = new_df["agent_id"].map(uuid_map)

    new_df["decision"] = 1

    return new_df

def rule_based_selection(df):
    rb_uuid = "rule_based_" + str(uuid.uuid4())
    new_df = df.copy()
    uuid_map = {
        old_id: rb_uuid
        for old_id in new_df["agent_id"].unique()
    }

    new_df["agent_id"] = new_df["agent_id"].map(uuid_map)

    indicators_data = read_from_json(config['cti_data_pool'])
    total_keys=[]
    for key in indicators_data.keys():
            total_keys.extend(list(indicators_data[key].keys()))
    unique_keys = list(set(total_keys))

    def rule_function(indicator):
        data={}
        for key1 in indicators_data.keys():
            if indicator == indicators_data[key1]["id"]:
                data = indicators_data[key1]
                break
        intersection_props= set(unique_keys) & set(list(data.keys()))

        indicator_timestamp=""
        if "created" in list(data.keys()):
            indicator_timestamp=data["created"]
        elif "valid_from" in list(data.keys()):
            indicator_timestamp=data["valid_from"]
        indicator_ts=pd.to_datetime(indicator_timestamp, utc=True).timestamp()
        current_ts = datetime.now().timestamp()
        threshold = 1.5
        quality_metric=(1000000000/(current_ts-indicator_ts))*(len(list(intersection_props))/len(list(unique_keys)))
        if quality_metric>threshold:
            return 1
        else:
            return 0

    new_df["decision"] = new_df["indicator"].apply(rule_function)
    return new_df


def  run(config):
    dfs=[]
    data=load_data(config)
    data1=random_selection(data)
    data2=heuristic_selection(data)
    data3=rule_based_selection(data)
    dfs.append(data)
    dfs.append(data1)
    dfs.append(data2)
    dfs.append(data3)
    df=pd.concat(dfs,ignore_index=True)
    df.to_csv(os.path.join(config['experiment_results_path'], "agents_data", f"exp0_comp_decided_actions.csv"), index=False)



if __name__=="__main__":
    config = read_config(CONFIG_PATH)
    run(config)