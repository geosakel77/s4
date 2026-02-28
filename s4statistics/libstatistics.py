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
from s4lib.libbase import read_from_json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve,roc_auc_score,precision_recall_curve,average_precision_score

def prepare_source_score_data(config):
    path=config['experiment_results_path']
    source_score_files=[]
    for file in os.listdir(path):
        if "source_score" in file:
            source_score_files.append(os.path.join(path,file))
    source_score_df_data={}
    for source_score_file in source_score_files:
        score_data=read_from_json(source_score_file)['history']
        sources_keys={}
        k=0
        for source in score_data[-1].keys():
            sources_keys[k]=source
            k+=1
        records=[]
        time=1
        for measurement in score_data:
            record= {'time': time}
            for key,item in sources_keys.items():
                record[f"src_{key}"]=measurement.get(item,0)
            time+=1
            records.append(record)

        df = pd.DataFrame(records)
        agent_cti_id=source_score_file.split("_")[4].split(".")[0]

        source_score_df_data[agent_cti_id]={"df":df,"source_keys":sources_keys}
    return source_score_df_data

def source_score_matrix_plot(source_score_df_data,config):
    for key,item in source_score_df_data.items():
        filename=os.path.join(config['images_path'],f"plots\\{key}.png")
        plot_source_matrix_comparison(item["df"],item["source_keys"],filename)


def plot_source_score_matrix_comparison_all(source_score_df_data,config):
    filename = os.path.join(config['images_path'],f"plots\\source_score_matrix_comparison_all.png")
    algos={"6fb16936-09b0-491b-8e6a-c3abbfc26f4a":"ES","add61679-8ecd-45b4-a77a-749c4c9dabb6":"QL","c370e907-9294-4755-a3a6-d756b4585180":"DAC"}

    min_length=100000

    for key in source_score_df_data.keys():
        if len(source_score_df_data[key]["df"])<min_length:
            min_length=len(source_score_df_data[key]["df"])
    for key in source_score_df_data.keys():
        df1_trim=source_score_df_data[key]["df"].iloc[:min_length]
        source_score_df_data[key]["df"]=df1_trim
        print(len(source_score_df_data[key]["df"]))
    plt.figure()
    for key,item in source_score_df_data.items():
        df=item["df"]
        source_keys=item["source_keys"]
        for key1 in source_keys.keys():
            sns.lineplot(data=df, x="time", y=f"src_{key1}", label=f"SRC {key1} - {algos[key]}")
    plt.xlabel("Time")
    plt.ylabel(f"Source Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def plot_source_matrix_comparison(df,source_keys,filename):
    plt.figure()
    for key in source_keys.keys():
        sns.lineplot(data=df,x="time",y=f"src_{key}",label=f"SRC {key}")
    plt.xlabel("Time")
    plt.ylabel(f"Source Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def prepare_agents_data(config):
    path=config['experiment_results_path']
    agents_files={}
    for file in os.listdir(path):
        if "agent" in file:
            agent_id=file.split("_")[0]
            if agent_id not in agents_files.keys():
                agents_files[agent_id]=[os.path.join(path,file)]
            else:
                agents_files[agent_id].append(os.path.join(path,file))
    agents_data={}
    for agent_id, agent_files in agents_files.items():
        agents_data[agent_id]=[]
        for file in agent_files:
            agents_data[agent_id].append(read_from_json(file))

    return agents_data

def agents_data_plots(agents_data,config):
    validation_data=read_from_json(config['validation_data_path'])

    for agent_id,data in agents_data.items():
        agent_data_plots(data,validation_data,agent_id,config)



def agent_data_plots(agents_data,validation_data,agent_id,config):
    for data in agents_data:
        rl_agent_plots(data,validation_data,agent_id,config)

    combined_rl_agent_plots(agents_data,validation_data,agent_id,config)

def combined_rl_agent_plots(agents_data,validation_data,agent_id,config):
    df_agents_episode_data, dm_keys = _combined_agent_data_to_dataframe(agents_data)
    _plot_combined_cumulative_reward(df_agents_episode_data,dm_keys,agent_id,config)

def _combined_agent_data_to_dataframe(agents_data):
    records=[]
    dm_keys=[]
    episode=1
    for i in range(len(agents_data[0]["episode_goals"])):
        record={"episode":episode}
        id_prv=0
        id_det=0
        id_res=0
        for data in agents_data:
            if data["dm_type"]==0:
                dm_id=f"Prev_{id_prv}"
                dm_keys.append(dm_id)
                record[dm_id]=data["episode_goals"][i]
                id_prv+=1
            elif data["dm_type"]==1:
                dm_id=f"Det_{id_det}"
                dm_keys.append(dm_id)
                record[dm_id] = data["episode_goals"][i]
                id_det+=1
            elif data["dm_type"]==2:
                dm_id=f"Res_{id_res}"
                dm_keys.append(dm_id)
                record[dm_id] = data["episode_goals"][i]
        records.append(record)
        episode+=1
    df = pd.DataFrame(records)
    return df, set(dm_keys)

def _plot_combined_cumulative_reward(dm_agents_episode_data,dm_keys,agent_id,config):
    filename = os.path.join(config['images_path'], f"plots\\{agent_id}_combined_cumulative_reward.png")
    plt.figure()
    for dm_key in dm_keys:
        sns.lineplot(data=dm_agents_episode_data,x="episode",y=dm_key,label=dm_key)
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def rl_agent_plots(rl_agent_data,validation_data,agent_id,config):
    print(rl_agent_data.keys())
    _plot_cumulative_reward(rl_agent_data['episode_goals'],rl_agent_data['dm_type'],rl_agent_data['dm_uuid'],agent_id,config)
    _plot_roc_auc_dm(rl_agent_data["decided_actions"],validation_data,rl_agent_data['dm_type'],rl_agent_data['dm_uuid'],agent_id,config)
    _plot_pr_rec_dm(rl_agent_data["decided_actions"],validation_data,rl_agent_data['dm_type'],rl_agent_data['dm_uuid'],agent_id,config)

def _plot_pr_rec_dm(decided_actions_data,validation_data,dm_type,dm_uuid,agent_id,config):
    filename = os.path.join(config['images_path'], f"plots\\{agent_id}_{dm_type}_{dm_uuid}_pres_recall.png")
    transformed_validation_data={}
    for key in validation_data.keys():
        transformed_validation_data[validation_data[key]['id']]=[validation_data[key]['0'],validation_data[key]['1'],validation_data[key]['2']]
    y_true=[]
    y_prob=[]
    for key in decided_actions_data.keys():
        y_prob.append(decided_actions_data[key])
        y_true.append(transformed_validation_data[key][dm_type])

    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    ap_score = average_precision_score(y_true, y_prob)

    plt.plot(recall, precision, label=f"AP = {ap_score:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def _plot_roc_auc_dm(decided_actions_data,validation_data,dm_type,dm_uuid,agent_id,config):
    filename = os.path.join(config['images_path'], f"plots\\{agent_id}_{dm_type}_{dm_uuid}_roc_auc.png")
    transformed_validation_data={}
    for key in validation_data.keys():
        transformed_validation_data[validation_data[key]['id']]=[validation_data[key]['0'],validation_data[key]['1'],validation_data[key]['2']]
    y_true=[]
    y_prob=[]
    for key in decided_actions_data.keys():
        y_prob.append(decided_actions_data[key])
        y_true.append(transformed_validation_data[key][dm_type])

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc_score = roc_auc_score(y_true, y_prob)

    plt.plot(fpr, tpr, label=f"AUC = {auc_score:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def _plot_cumulative_reward(rl_agent_data,dm_type,dm_uuid,agent_id,config):
    filename = os.path.join(config['images_path'], f"plots\\{agent_id}_{dm_type}_{dm_uuid}_cumulative_reward.png")
    episodes= np.arange(1, len(rl_agent_data)+1)
    df = pd.DataFrame({
        "episode":episodes,
        "goals":rl_agent_data,
    })
    plt.figure()
    sns.lineplot(data=df, x="episode", y="goals", label="Reward")
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()



def plot_cumulative_reward_all_types(agents_data,config):
    filename = os.path.join(config['images_path'], f"plots\\combined_cumulative_reward_all.png")
    episodes=0
    for agent_id,data in agents_data.items():
        for dm_policy in data:
           episodes=len(dm_policy['episode_goals'])
           break
    records = []
    dm_keys = []
    episode = 1
    for i in range(episodes):
        record = {"episode": episode}
        id_prv = 0
        id_det = 0
        id_res = 0
        for agent_id,dm_policy in agents_data.items():
            for data in dm_policy:
                if data["dm_type"] == 0:
                    dm_id = f"Prev_{data['algo']}"
                    dm_keys.append(dm_id)
                    record[dm_id] = data["episode_goals"][i]
                    id_prv += 1
                elif data["dm_type"] == 1:
                    dm_id = f"Det_{data['algo']}"
                    dm_keys.append(dm_id)
                    record[dm_id] = data["episode_goals"][i]
                    id_det += 1
                elif data["dm_type"] == 2:
                    dm_id = f"Res_{data['algo']}"
                    dm_keys.append(dm_id)
                    record[dm_id] = data["episode_goals"][i]
        records.append(record)
        episode += 1
    df = pd.DataFrame(records)
    print("start plotting")
    df_trim=df.iloc[:200]
    dm_keys_u=set(dm_keys)
    plt.figure()
    for dm_key in dm_keys_u:
        sns.lineplot(data=df_trim, x="episode", y=dm_key, label=dm_key)
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()
    filename1 = os.path.join(config['images_path'], f"plots\\combined_cumulative_reward_all_prev.png")
    plt.figure()
    for dm_key in dm_keys_u:
        if "Prev" in dm_key:
            sns.lineplot(data=df_trim, x="episode", y=dm_key, label=dm_key)
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename1)
    plt.show()
    filename2 = os.path.join(config['images_path'], f"plots\\combined_cumulative_reward_all_det.png")
    plt.figure()
    for dm_key in dm_keys_u:
        if "Det" in dm_key:
            sns.lineplot(data=df_trim, x="episode", y=dm_key, label=dm_key)
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename2)
    plt.show()
    filename3 = os.path.join(config['images_path'], f"plots\\combined_cumulative_reward_all_res.png")
    plt.figure()
    for dm_key in dm_keys_u:
        if "Res" in dm_key:
            sns.lineplot(data=df_trim, x="episode", y=dm_key, label=dm_key)
    plt.xlabel("Episode")
    plt.ylabel(f"Cumulative Reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename3)
    plt.show()

def plot_cumulative_decisions(agents_data,config):
    filename = os.path.join(config['images_path'], f"plots\\combined_cumulative_decisions_all.png")
    min_value=10000000
    policies=[]

    for agent_id, data in agents_data.items():
        for dm_policy in data:
            records=[]
            for key, item in dm_policy["decided_actions"].items():
                record={"ind":key,"value":item}
                records.append(record)
            dm_policy['decided_actions'] = pd.DataFrame(records)
            if len(dm_policy['decided_actions'])<min_value:
                min_value=len(dm_policy['decided_actions'])
            policies.append(dm_policy)
    policies_trimmed=[]
    for dm_policy in policies:
        dm_policy['decided_actions'] = dm_policy['decided_actions'].iloc[:min_value]
        policies_trimmed.append(dm_policy)
    policies_final=[]

    for dm_policy in policies_trimmed:
        send= (dm_policy['decided_actions']["value"]==0).sum()
        not_send= (dm_policy['decided_actions']["value"]==1).sum()
        new_df=pd.DataFrame([{"send":send, "not_send":not_send}])
        dm_policy['decided_actions'] = new_df
        dm_policy.pop("episode_goals")
        dm_policy.pop("num_q_entries")
        dm_policy.pop("obs_actions")
        if dm_policy["dm_type"]==0:
            dm_policy["dm_type"]="Prev"
        elif dm_policy["dm_type"]==1:
            dm_policy["dm_type"]="Det"
        elif dm_policy["dm_type"]==2:
            dm_policy["dm_type"]="Res"
        if "q" in dm_policy.keys():
            dm_policy.pop("q")
        elif 'w_pi' in dm_policy.keys():
            dm_policy.pop("w_pi")
        policies_final.append(dm_policy)


    records=[]
    for dm_policy in policies_final:
        record={"dm_type":dm_policy["dm_type"],'algo':dm_policy["algo"],'send':dm_policy["decided_actions"].at[0,"send"],'not_send':dm_policy["decided_actions"].at[0,"not_send"]}
        records.append(record)

    df = pd.DataFrame(records)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(df)

    df_melt = df.melt(
        id_vars=["dm_type", "algo"],
        value_vars=["send", "not_send"],
        var_name="action",
        value_name="count"
    )

    g = sns.catplot(
        data=df_melt,
        col="algo",  # Level 1
        x="dm_type",  # Level 2
        y="count",
        hue="action",  # Level 3
        kind="bar",
        height=5,
        aspect=1.1,
        errorbar=None
    )
    g.set_axis_labels("", "CTI Products")
    g.set_titles("Algorithm = {col_name}")

    g._legend.set_title("action")
    plt.subplots_adjust(top=0.95)
    plt.savefig(filename)
    plt.show()