from s4lib.libbase import read_from_json
from s4config.libconstants import DM_TYPES
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve,auc,roc_auc_score,precision_recall_curve,average_precision_score


def plot_average_source_score(config,exp):
    dfs=[]
    for expa in exp:
        source_scores_filename = os.path.join(config['experiment_results_path'], "source_score", f"{expa}_source_score.csv")
        source_scores_df = pd.read_csv(source_scores_filename)
        dfs.append(source_scores_df)

    df_all = pd.concat(dfs,ignore_index=True)
    print(df_all)
    sources = [col for col in df_all.columns if col.startswith('src_')]
    print(sources)
    avg_df = (
        df_all.groupby(["algo", "time"])[sources]
        .mean()
        .reset_index()
    )
    print(avg_df)
    os.makedirs(os.path.join(config['images_path'], "plots", "expext"), exist_ok=True)
    for algo in avg_df["algo"].unique():
        d = avg_df[avg_df["algo"] == algo]
        plt.figure(figsize=(10, 5))
        for src in sources:
            plt.plot(
                d["time"],
                d[src],
                linewidth=2,
                label=src
            )
        plt.title(f"{algo} - Average Source Score")
        plt.xlabel("Time")
        plt.ylabel("Average Source Score")
        plt.grid(alpha=0.3)
        plt.legend(title="Source")
        plt.tight_layout()
        plt.show()
        plot_filename = os.path.join(config['images_path'], "plots","expext", f"{algo}_average_source_score.png")
        plt.savefig(plot_filename)

    fig, axes = plt.subplots(
        nrows=len(avg_df["algo"].unique()),
        figsize=(12, 10),
        sharex=True,
        sharey=True
    )

    for ax, algo in zip(axes, sorted(avg_df["algo"].unique())):

        d = avg_df[avg_df["algo"] == algo]

        for src in sources:
            ax.plot(
                d["time"],
                d[src],
                linewidth=2,
                label=src
            )

        ax.set_title(algo)
        ax.set_ylabel("Average Score")
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Time")
    axes[0].legend(title="Source")

    plt.tight_layout()
    plt.show()
    plot_filename = os.path.join(config['images_path'], "plots", "expext", f"all_algo_average_source_score.png")
    plt.savefig(plot_filename)

def plot_confidence_intervals_source_score(config,exp):
    dfs=[]
    for expa in exp:
        source_scores_filename = os.path.join(config['experiment_results_path'], "source_score", f"{expa}_source_score.csv")
        source_scores_df = pd.read_csv(source_scores_filename)
        dfs.append(source_scores_df)

    df_all = pd.concat(dfs,ignore_index=True)
    src_cols = [col for col in df_all.columns if col.startswith('src_')]
    stats = (
        df_all.groupby(["algo", "time"])[src_cols]
        .agg(['mean', 'std', 'count'])
    )

    # Flatten MultiIndex columns
    stats.columns = ['_'.join(col) for col in stats.columns]
    stats = stats.reset_index()

    # Compute 95% confidence intervals
    for src in src_cols:
        stats[f'{src}_ci'] = (
                1.96
                * stats[f'{src}_std']
                / np.sqrt(stats[f'{src}_count'])
        )
    print(stats)

    for algo in sorted(stats["algo"].unique()):

        d = stats[stats["algo"] == algo]

        plt.figure(figsize=(10, 5))

        for src in src_cols:
            mean = d[f"{src}_mean"]
            ci = d[f"{src}_ci"]

            plt.plot(
                d["time"],
                mean,
                linewidth=2,
                label=src
            )

            plt.fill_between(
                d["time"],
                mean - ci,
                mean + ci,
                alpha=0.25
            )

        plt.title(f"{algo} - Average Source Score (95% CI)")
        plt.xlabel("Time")
        plt.ylabel("Average Source Score")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    algos = sorted(stats["algo"].unique())

    fig, axes = plt.subplots(
        nrows=len(algos),
        ncols=1,
        figsize=(12, 4 * len(algos)),
        sharex=True,
        sharey=True
    )

    # If there is only one algorithm
    if len(algos) == 1:
        axes = [axes]

    for ax, algo in zip(axes, algos):

        d = stats[stats["algo"] == algo]

        for src in src_cols:
            mean = d[f"{src}_mean"].values
            ci = d[f"{src}_ci"].values

            ax.plot(
                d["time"],
                mean,
                linewidth=2,
                label=src
            )

            ax.fill_between(
                d["time"],
                mean - ci,
                mean + ci,
                alpha=0.20
            )

        ax.set_title(f"{algo}")
        ax.set_ylabel("Average Source Score")
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Time")

    # Single legend for all subplots
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="center",
        ncol=len(src_cols),
        bbox_to_anchor=(0.5, 1.02)
    )

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()



def plot_average_cumulative_reward(config,exp):
    dfs=[]
    for expa in exp:
        agent_goals_filename = os.path.join(config['experiment_results_path'], "agents_data",
                                                  f"{expa}_episode_goals.csv")
        agents_goals_df = pd.read_csv(agent_goals_filename)
        dfs.append(agents_goals_df)
    df = pd.concat(dfs,ignore_index=True)
    metric="cumulative_goal"
    stats = (
        df.groupby(["algo", "dm_type", "episode"])[metric]
        .agg(
            mean="mean",
            std="std",
            n="count"
        )
        .reset_index()
    )

    stats["se"] = stats["std"] / np.sqrt(stats["n"])
    stats["ci95"] = 1.96 * stats["se"]
    algorithms = sorted(stats["algo"].unique())
    dm_types = sorted(stats["dm_type"].unique())

    fig, axes = plt.subplots(
        len(dm_types),
        1,
        figsize=(12, 4 * len(dm_types)),
        sharex=True,
        sharey=True
    )

    if len(dm_types) == 1:
        axes = [axes]

    for ax, dm_type in zip(axes, dm_types):

        d_dm = stats[stats["dm_type"] == dm_type]

        for algo in algorithms:
            d = d_dm[d_dm["algo"] == algo]

            ax.plot(
                d["episode"],
                d["mean"],
                linewidth=2,
                label=algo
            )

            ax.fill_between(
                d["episode"],
                d["mean"] - d["ci95"],
                d["mean"] + d["ci95"],
                alpha=0.20
            )

        ax.set_title(f"DM: {dm_type}")
        ax.set_ylabel("Cumulative Reward")
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Episode")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=len(algorithms),
        bbox_to_anchor=(0.5, 1.02)
    )

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()

    colors = {
        "QL": "#1f77b4",
        "ES": "#ff7f0e",
        "DAC": "#2ca02c"
    }

    for dm_type in sorted(stats["dm_type"].unique()):

        plt.figure(figsize=(10, 6))

        d_dm = stats[stats["dm_type"] == dm_type]

        for algo in sorted(d_dm["algo"].unique()):
            d = d_dm[d_dm["algo"] == algo].sort_values("episode")

            plt.plot(
                d["episode"],
                d["mean"],
                label=algo,
                linewidth=2.5,
                color=colors.get(algo)
            )

            plt.fill_between(
                d["episode"],
                d["mean"] - d["ci95"],
                d["mean"] + d["ci95"],
                color=colors.get(algo),
                alpha=0.20
            )

        plt.title(f"DM:{dm_type}")
        plt.xlabel("Episode")
        plt.ylabel("Cumulative Reward")
        plt.grid(True, alpha=0.3)
        plt.legend(title="Algorithm")
        plt.tight_layout()
        plt.show()


def plot_comparison(config,data):
    pass

def plot_analysis(config,exp):
    #plot_average_source_score(config,exp)
    #plot_confidence_intervals_source_score(config,exp)
    #plot_average_cumulative_reward(config,exp)
    plot_comparison(config,data)