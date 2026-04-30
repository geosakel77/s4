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
    print("Decided Actions DF:")
    print(df_decided_actions.head())
    print("Episode Goals DF:")
    print(df_episode_goals.head())
    df_decided_actions.to_csv(os.path.join(config['experiment_results_path'], "agents_data", f"{exp}_decided_actions.csv"), index=False)
    df_episode_goals.to_csv(os.path.join(config['experiment_results_path'], "agents_data", f"{exp}_episode_goals.csv"), index=False)

def prepare_validation_data(config):
    validation_data_filename = os.path.join(config["validation_data_dir"], "validation_data.json")
    data = read_from_json(validation_data_filename)
    agent_id="heuristic_agent_0000"
    algo="Heuristic"
    data_list=[]
    for key, value in data.items():
        for key1, item1 in value.items():
            if key1 == "0" or key1 == "1" or key1 == "2":
                row = {"agent_id": agent_id, "algo": algo, "dm_type": DM_TYPES[int(key1) + 1], "indicator": value["id"],
                       "decision": item1}
                data_list.append(row)

    df=pd.DataFrame(data_list)
    print(df.head())
    os.makedirs(os.path.join(config['experiment_results_path'], "validation_data"), exist_ok=True)
    df.to_csv(os.path.join(config['experiment_results_path'], "validation_data", f"heuristic_decided_actions.csv"), index=False)

def plot_source_score_comparison_per_algo(df,sources,prefix,config):
    # Plotting source score comparison per algorithm
    for src_col in sources:
        df_common = filter_common_time(df,src_col)
        sns.lineplot(
            data=df_common,
            x='time',
            y=src_col,
            hue='algo',
            estimator='mean'  # if multiple agents per time
        )

        plt.xlabel('Time')
        plt.ylabel('Score')
        plt.legend(title='Algorithm')
        plt.show()
        os.makedirs(os.path.join(config['images_path'],"plots", prefix),exist_ok=True)
        plot_filename = os.path.join(config['images_path'], "plots", prefix,f"{prefix}_{src_col}_comparison_per_algo.png")
        plt.savefig(plot_filename)

def filter_common_time(df,src_col):
    df_plot = df[["time", "algo",src_col]].dropna()

    # Find time points where all algos exist
    algo_count_per_time = df_plot.groupby("time")["algo"].nunique()
    common_times = algo_count_per_time[
        algo_count_per_time == df_plot["algo"].nunique()
        ].index

    # Filter only common time points
    df_common = df_plot[df_plot["time"].isin(common_times)]
    return df_common

def plot_3d_score_comparison_per_algo(df,sources,prefix,config):
    for src_col in sources:
        df_common = filter_common_time(df,src_col)
        pivot_df = df_common.pivot(
            index="algo",
            columns="time",
            values=src_col
        )
        algos = list(pivot_df.index)
        times = list(pivot_df.columns)
        X, Y = np.meshgrid(times, range(len(algos)))
        Z = pivot_df.values

        fig = plt.figure(figsize=(12, 7))
        ax = fig.add_subplot(111, projection="3d")

        surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="k", alpha=0.85)

        ax.set_xlabel("Time")
        ax.set_ylabel("Algorithm")
        ax.set_zlabel(f"{src_col}")

        ax.set_yticks(range(len(algos)))
        ax.set_yticklabels(algos)

        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, label="Score")

        os.makedirs(os.path.join(config['images_path'],"plots", prefix),exist_ok=True)
        plot_filename = os.path.join(config['images_path'], "plots", prefix,f"{prefix}_{src_col}_3d_comparison_per_algo.png")
        plt.savefig(plot_filename)


def plot_all_sources_score(df,prefix,config):
    sns.relplot(
        data=df,
        x='time',
        y='score',
        hue='algo',
        col='source',
        kind='line',
        col_wrap=3,
        height=4
    )

    plt.show()
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix, f"{prefix}_all_sources_comparison.png")
    plt.savefig(plot_filename)

def plot_all_sources_score_combine(df,prefix,config):
    sns.lineplot(
        data=df,
        x='time',
        y='score',
        hue='algo',
        style='source'
    )
    plt.show()

    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix, f"{prefix}_all_sources_comparison_per_algo.png")
    plt.savefig(plot_filename)

def plot_source_score(config,exp):
    source_scores_filename = os.path.join(config['experiment_results_path'], "source_score", f"{exp}_source_score.csv")
    source_scores_df = pd.read_csv(source_scores_filename)
    sources = [col for col in source_scores_df.columns if col.startswith('src_')]

    df_long = source_scores_df.melt(
        id_vars=['agent_id', 'time', 'algo'],
        value_vars=[col for col in source_scores_df.columns if col.startswith('src_')],
        var_name='source',
        value_name='score'
    )
    df_long = df_long.dropna(subset=['score'])

    # Compute time range per source
    time_ranges = df_long.groupby('algo')['time'].agg(['min', 'max'])
    print(time_ranges)
    # Find common overlap window
    common_start = time_ranges['min'].max()
    common_end = time_ranges['max'].min()

    # Filter dataset to overlap window
    df_long_filtered = df_long[
        (df_long['time'] >= common_start) &
        (df_long['time'] <= common_end)
        ]

    plot_source_score_comparison_per_algo(df=source_scores_df,sources=sources,prefix=exp,config=config)
    plot_3d_score_comparison_per_algo(df=source_scores_df,sources=sources,prefix=exp,config=config)
    plot_all_sources_score(df_long_filtered,exp,config)
    plot_all_sources_score_combine(df_long_filtered,exp,config)



def plot_exp_analysis(config,exp):
    plot_source_score(config,exp)