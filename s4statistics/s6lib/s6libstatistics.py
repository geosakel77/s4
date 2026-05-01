from s4lib.libbase import read_from_json
from s4config.libconstants import DM_TYPES
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve,auc,roc_auc_score,precision_recall_curve,average_precision_score
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
                episode+=1

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
        g=sns.lineplot(
            data=df_common,
            x='time',
            y=src_col,
            hue='algo',
            estimator='mean'  # if multiple agents per time
        )

        plt.xlabel('Time')
        plt.ylabel('Score')
        plt.legend(title='Algorithm')
        plt.tight_layout()
        plt.show()
        os.makedirs(os.path.join(config['images_path'],"plots", prefix),exist_ok=True)
        plot_filename = os.path.join(config['images_path'], "plots", prefix,f"{prefix}_{src_col}_comparison_per_algo.png")
        g.figure.savefig(plot_filename)

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
    g=sns.relplot(
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
    g.figure.savefig(plot_filename)

def plot_all_sources_score_combine(df,prefix,config):
    g=sns.lineplot(
        data=df,
        x='time',
        y='score',
        hue='algo',
        style='source'
    )
    plt.show()

    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix, f"{prefix}_all_sources_comparison_per_algo.png")
    g.figure.savefig(plot_filename)

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

def plot_cumulative_goal_per_episode(df_agg,prefix,config):
    g=sns.relplot(
        data=df_agg,
        x='episode',
        y='cumulative_goal',
        hue='algo',
        col='dm_type',
        kind='line',
        col_wrap=3,
        height=4,
        facet_kws={'sharey': True, 'sharex': True}
    )

    plt.show()
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                 f"{prefix}_cumulative_goal_per_episode.png")
    g.figure.savefig(plot_filename)

def plot_goal_per_episode(df_agg,prefix,config):
    g=sns.relplot(
        data=df_agg,
        x='episode',
        y='goal',
        hue='algo',
        col='dm_type',
        kind='line',
        col_wrap=3,
        height=4,
        facet_kws={'sharey': True, 'sharex': True}
    )

    plt.show()
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                 f"{prefix}_goal_per_episode.png")
    g.figure.savefig(plot_filename)

def plot_decisions_per_dm(df,prefix,config):
    df['decision_label'] = df['decision'].map({0: 'send', 1: 'not send'})
    df['dm_idx'] = (
        df.groupby(['algo', 'dm_type'])['dm_uuid']
        .transform(lambda x: pd.factorize(x)[0] + 1)
    )

    df['dm_label'] = (
            'dm_' + df['dm_type'].astype(str).str.lower().str[:3] + '_' + df['dm_idx'].astype(str)
    )

    df_plot = (
        df.groupby(['algo', 'dm_label', 'decision_label'])
        .size()
        .reset_index(name='count')
    )
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    g = sns.catplot(
        data=df_plot,
        x='dm_label',
        y='count',
        hue='decision_label',
        col='algo',
        kind='bar',
        height=4,
        aspect=1.3
    )
    plt.legend(title="Decision")
    plt.show()
    plot_filename1 = os.path.join(config['images_path'], "plots", prefix,
                                 f"{prefix}_decisions_per_dm_and_algo.png")
    g.figure.savefig(plot_filename1)

    g1=sns.barplot(
        data=df_plot,
        x='dm_label',
        y='count',
        hue='decision_label'
    )
    plt.legend(title="Decision")
    plt.show()
    plot_filename2 = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_total_decisions_per_dm_in_all_algos.png")
    g1.figure.savefig(plot_filename2)

    df_plot['ratio'] = (
            df_plot['count'] /
            df_plot.groupby(['algo', 'dm_label'])['count'].transform('sum')
    )
    g2=sns.catplot(
        data=df_plot,
        x='dm_label',
        y='ratio',
        hue='decision_label',
        col='algo',
        kind='bar',
        height=4,
        aspect=1.3
    )
    plt.legend(title="Decision")
    plt.show()
    plot_filename3 = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_decisions_per_dm_and_algo_ratio.png")
    g2.figure.savefig(plot_filename3)


def plot_decisions_per_dm_type(df,prefix,config):
    df['decision_label'] = df['decision'].map({0: 'send', 1: 'not send'})
    df_type = (
        df.groupby(['algo', 'dm_type', 'decision_label'])
        .size()
        .reset_index(name='count')
    )
    df_type['ratio'] = (
            df_type['count'] /
            df_type.groupby(['algo', 'dm_type'])['count'].transform('sum')
    )
    g = sns.catplot(
        data=df_type,
        x='dm_type',
        y='ratio',
        hue='decision_label',
        col='algo',
        kind='bar',
        height=4,
        aspect=1.2
    )
    plt.legend(title="Decision")
    g.set_titles("Algo: {col_name}")
    g.set_axis_labels("DM Type", "Decision Ratio")

    plt.show()
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_decisions_per_dm_type_and_algo_ratio.png")
    g.figure.savefig(plot_filename)
    g1=sns.barplot(
        data=df_type,
        x='dm_type',
        y='ratio',
        hue='decision_label'
    )
    plt.ylabel("Ratio")
    plt.legend(title="Decision")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()
    plot_filename1 = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_decisions_per_dm_type_ratio.png")
    g1.figure.savefig(plot_filename1)

def plot_comparison_rl_heuristic(df_rl,df_h,prefix,config):
    df_rl["method"] = "RL"
    df_h["method"] = "Heuristic"

    common_cols = ["algo", "dm_type", "decision"]

    df_compare = pd.concat([
        df_rl[common_cols],
        df_h[common_cols]
    ], ignore_index=True)

    df_compare["decision_label"] = df_compare["decision"].map({
        0: "send",
        1: "not send"
    })
    summary = (
        df_compare
        .groupby(["algo", "dm_type", "decision_label"])
        .size()
        .reset_index(name="count")
    )
    summary["percentage"] = (
        summary
        .groupby(["algo", "dm_type"])["count"]
        .transform(lambda x: 100 * x / x.sum())
    )

    summary["percentage"] = (
        summary
        .groupby(["algo", "dm_type"])["count"]
        .transform(lambda x: 100 * x / x.sum())
    )

    g = sns.catplot(
        data=summary,
        x="dm_type",
        y="percentage",
        hue="decision_label",
        col="algo",
        kind="bar",
        col_wrap=3,
        height=4,
        aspect=1.3,
        errorbar=None,
        hue_order=["send", "not send"]
    )

    g.set_axis_labels("DM Type", "Percentage (%)")
    g.set_titles("Algo: {col_name}")
    g._legend.set_title("Decision")

    plt.show()
    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_comparison_rl_heuristics.png")
    g.figure.savefig(plot_filename)

def plot_comparison_rl_heuristic_common_indicators(df_rl,df_h,prefix,config):
    common_indicators = set(df_rl["indicator"]).intersection(df_h["indicator"])
    decision_map = {
        0: "send",
        1: "not send"
    }
    df_rl_c = df_rl.copy()
    df_h_c = df_h.copy()

    df_rl_c["indicator_norm"] = df_rl_c["indicator"].astype(str).str.strip().str.lower()
    df_h_c["indicator_norm"] = df_h_c["indicator"].astype(str).str.strip().str.lower()

    common_indicators = set(df_rl_c["indicator_norm"]) & set(df_h_c["indicator_norm"])

    df_rl_c = df_rl_c[df_rl_c["indicator_norm"].isin(common_indicators)]
    df_h_c = df_h_c[df_h_c["indicator_norm"].isin(common_indicators)]

    df_merged = df_rl_c.merge(
        df_h_c,
        on=["indicator_norm", "dm_type"],
        suffixes=("_rl", "_heur")
    )

    df_merged["decision_rl_label"] = df_merged["decision_rl"].map(decision_map)
    df_merged["decision_heur_label"] = df_merged["decision_heur"].map(decision_map)

    df_merged["agreement"] = df_merged["decision_rl"] == df_merged["decision_heur"]

    summary = (
        df_merged
        .groupby(["algo_rl", "dm_type", "agreement"])
        .size()
        .reset_index(name="count")
    )
    summary["percentage"] = (
        summary
        .groupby(["algo_rl", "dm_type"])["count"]
        .transform(lambda x: 100 * x / x.sum())
    )

    summary["agreement_label"] = summary["agreement"].map({
        True: "Agreement",
        False: "Disagreement"
    })

    if summary.empty:
        print("No matching rows after merge.")
    else:
        g = sns.catplot(
            data=summary,
            x="dm_type",
            y="percentage",
            hue="agreement_label",
            col="algo_rl",
            kind="bar",
            col_wrap=3,
            height=4,
            aspect=1.3,
            errorbar=None
        )

        g.set_axis_labels("DM Type", "Percentage (%)")
        g.set_titles("Algorithm: {col_name}")
        g._legend.set_title("RL vs Heuristic")

        plt.show()
        os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
        plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                  f"{prefix}_comparison_rl_heuristic_commom_indicators.png")
        g.figure.savefig(plot_filename)

        plot_roc_curve_rl_heuristic(df_merged,prefix,config)

def plot_roc_curve_rl_heuristic(df_merged,prefix,config):
    y_true = df_merged["decision_heur"]
    y_pred = df_merged["decision_rl"]
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    f1=plt.figure()

    plt.plot(fpr, tpr, marker='o', label=f"RL vs Heuristic (AUC={roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], 'k--')

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC (Heuristic as Ground Truth)")
    plt.legend()

    plt.grid()
    plt.show()

    os.makedirs(os.path.join(config['images_path'], "plots", prefix), exist_ok=True)
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                 f"{prefix}_roc_auc_rl_methods_heuristic.png")

    f1.savefig(plot_filename)
    f2=plt.figure()

    for algo in df_merged["algo_rl"].unique():
        df_a = df_merged[df_merged["algo_rl"] == algo]

        if len(df_a) == 0:
            continue

        fpr, tpr, _ = roc_curve(
            df_a["decision_heur"],
            df_a["decision_rl"]
        )

        roc_auc = auc(fpr, tpr)

        plt.plot(fpr, tpr, marker='o', label=f"{algo} (AUC={roc_auc:.2f})")

    plt.plot([0, 1], [0, 1], 'k--')

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.grid()
    plt.show()
    plot_filename = os.path.join(config['images_path'], "plots", prefix,
                                 f"{prefix}_roc_auc_rl_algos_heuristic.png")
    f2.savefig(plot_filename)

def plot_agent_analysis(config,exp):
    agent_decided_actions_filename = os.path.join(config['experiment_results_path'], "agents_data", f"{exp}_decided_actions.csv")
    agents_da_df = pd.read_csv(agent_decided_actions_filename)
    agent_goals_filename = os.path.join(config['experiment_results_path'], "agents_data",
                                                  f"{exp}_episode_goals.csv")
    agents_goals_df = pd.read_csv(agent_goals_filename)
    heuristic_filename=os.path.join(config['experiment_results_path'], "validation_data", f"heuristic_decided_actions.csv")
    heuristic_data_df=pd.read_csv(heuristic_filename)
    df_agg = (
        agents_goals_df.groupby(['algo', 'dm_type', 'episode'])['cumulative_goal'].mean().reset_index()
    )
    plot_cumulative_goal_per_episode(df_agg,exp,config)

    df_agg1 = (
        agents_goals_df.groupby(['algo', 'dm_type', 'episode'])['goal'].mean().reset_index()
    )
    plot_goal_per_episode(df_agg1,exp,config)
    plot_decisions_per_dm(agents_da_df,exp,config)
    plot_decisions_per_dm_type(agents_da_df,exp,config)
    plot_comparison_rl_heuristic(agents_da_df,heuristic_data_df,exp,config)
    plot_comparison_rl_heuristic_common_indicators(agents_da_df,heuristic_data_df,exp,config)

def plot_exp_analysis(config,exp):
    plot_source_score(config,exp)
    plot_agent_analysis(config,exp)