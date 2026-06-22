from s4lib.libbase import read_from_json
from s4config.libconstants import DM_TYPES
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

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


def plot_comparison(config,df):
    plot_df = df.copy()

    # 0 = send, 1 = not_send
    plot_df["action"] = plot_df["decision"].map({
        1: "send",
        0: "not_send"
    })

    # Classify agent/method
    def classify_method(row):
        agent_id = str(row["agent_id"])

        if agent_id.startswith("heuristic"):
            return "Heuristic"
        elif agent_id.startswith("rule_based"):
            return "Rule-based"
        elif agent_id.startswith("random"):
            return "Random"
        else:
            return row["algo"]  # QL, ES, DAC

    plot_df["method"] = plot_df.apply(classify_method, axis=1)
    # Count decisions
    counts = (
        plot_df
        .groupby(["algo","method", "dm_type", "action"])
        .size()
        .reset_index(name="count")
    )
    print(counts)
    # Convert to percentages per method and dm_type
    counts["percentage"] = (
        counts.groupby(["algo","method", "dm_type"])["count"]
        .transform(lambda x: 100 * x / x.sum())
    )

    # Ensure consistent order
    rl_algorithms = ["ES", "QL", "DAC"]
    dm_order = ["Responsive", "Preventive", "Detective"]
    method_order_base = ["Heuristic", "Rule-based", "Random"]

    fig, axes = plt.subplots(
        1,
        len(rl_algorithms),
        figsize=(22, 6),
        sharey=True
    )

    for ax, algo in zip(axes, rl_algorithms):

        selected_methods = [algo] + method_order_base

        d = counts[counts["method"].isin(selected_methods)].copy()

        d["group"] = d["dm_type"] + "\n" + d["method"]

        group_order = []
        for dm_type in dm_order:
            for method in selected_methods:
                group_order.append(f"{dm_type}\n{method}")

        sns.barplot(
            data=d,
            x="group",
            y="percentage",
            hue="action",
            order=group_order,
            hue_order=["send", "not_send"],
            ax=ax
        )

        ax.set_title(f"Algorithm = {algo}")
        ax.set_xlabel("")
        ax.set_ylabel("Decision Percentage (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_average_actionability(config,df):
    """
    summary = (
        df.groupby(["algo", "indicator"])["decision"]
        .sum()  # since 1 = Send
        .reset_index(name="send_count")
    )

    # Convert to categories
    summary["category"] = summary["send_count"].map({
        0: "0 DMs",
        1: "1 DM",
        2: "2 DMs",
        3: "3 DMs"
    })

    fig, axes = plt.subplots(
        1,
        len(summary.algo.unique()),
        figsize=(15, 5),
        sharey=True
    )

    for ax, algo in zip(axes, sorted(summary.algo.unique())):
        sns.countplot(
            data=summary[summary.algo == algo],
            x="category",
            order=["0 DMs", "1 DM", "2 DMs", "3 DMs"],
            ax=ax
        )

        ax.set_title(algo)
        ax.set_xlabel("Number of Defense Mechanisms")
        ax.set_ylabel("Number of Indicators")

    plt.tight_layout()
    plt.show()
    """
    decision = 1  # Send
    decision = 0  # Not Send

    send_summary = (
        df.groupby(["algo", "indicator"])["decision"]
        .sum()
        .reset_index(name="send_count")
    )

    send_summary["category"] = send_summary["send_count"].map({
        0: "0 DMs",
        1: "1 DM",
        2: "2 DMs",
        3: "3 DMs"
    })

    category_order = ["0 DMs", "1 DM", "2 DMs", "3 DMs"]
    algos = sorted(send_summary["algo"].unique())
    fig, axes = plt.subplots(
        1,
        len(algos),
        figsize=(5 * len(algos), 5),
        sharey=True
    )

    if len(algos) == 1:
        axes = [axes]

    for ax, algo in zip(axes, algos):
        sns.countplot(
            data=send_summary[send_summary["algo"] == algo],
            x="category",
            order=category_order,
            ax=ax
        )

        ax.set_title(algo)
        ax.set_xlabel("Number of DM types receiving the indicator")
        ax.set_ylabel("Number of Indicators")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()
    plot_counts = (
        send_summary
        .groupby(["algo", "category"])
        .size()
        .reset_index(name="count")
    )

    plot_counts["category"] = pd.Categorical(
        plot_counts["category"],
        categories=category_order,
        ordered=True
    )

    fig, axes = plt.subplots(
        1,
        len(algos),
        figsize=(5 * len(algos), 5),
        sharex=True
    )

    if len(algos) == 1:
        axes = [axes]

    for ax, algo in zip(axes, algos):

        d = (
            plot_counts[plot_counts["algo"] == algo]
            .sort_values("category")
        )

        y_pos = range(len(d))

        ax.hlines(
            y=y_pos,
            xmin=0,
            xmax=d["count"],
            linewidth=2
        )

        ax.plot(
            d["count"],
            y_pos,
            "o",
            markersize=8
        )

        for y, count in zip(y_pos, d["count"]):
            ax.text(
                count,
                y,
                f" {count}",
                va="center"
            )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(d["category"])
        ax.set_title(algo)
        ax.set_xlabel("Number of Indicators")
        ax.grid(axis="x", alpha=0.3)

    axes[0].set_ylabel("Number of DM types receiving the indicator")

    plt.tight_layout()
    plt.show()


    # Keep only sent indicators
    sent = df[df["decision"] == 1]

    # Count flows
    flows = (
        sent.groupby(["algo", "dm_type"])
        .size()
        .reset_index(name="count")
    )

    algos = sorted(flows["algo"].unique())
    dms = ["Responsive", "Preventive", "Detective"]

    labels = algos + dms

    algo_idx = {a: i for i, a in enumerate(algos)}
    dm_idx = {d: len(algos) + i for i, d in enumerate(dms)}

    source = flows["algo"].map(algo_idx)
    target = flows["dm_type"].map(dm_idx)
    value = flows["count"]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    ))

    fig.update_layout(
        title="CTI Dissemination per Algorithm",
        font_size=13
    )

    fig.show()
    send_profile = (
        df.groupby(["algo", "indicator"])["decision"]
        .sum()
        .reset_index(name="send_count")
    )

    send_profile["send_category"] = send_profile["send_count"].map({
        0: "0 DMs",
        1: "1 DM",
        2: "2 DMs",
        3: "3 DMs"
    })

    # --------------------------------------------------
    # 2. Count flows: Algorithm -> Send Category
    # --------------------------------------------------

    flows = (
        send_profile
        .groupby(["algo", "send_category"])
        .size()
        .reset_index(name="count")
    )

    # --------------------------------------------------
    # 3. Build Sankey nodes
    # --------------------------------------------------

    algos = sorted(flows["algo"].unique())
    categories = ["0 DMs", "1 DM", "2 DMs", "3 DMs"]

    labels = algos + categories

    algo_idx = {algo: i for i, algo in enumerate(algos)}
    cat_idx = {
        cat: len(algos) + i
        for i, cat in enumerate(categories)
    }

    flows["source"] = flows["algo"].map(algo_idx)
    flows["target"] = flows["send_category"].map(cat_idx)

    # --------------------------------------------------
    # 4. Plot Sankey diagram
    # --------------------------------------------------

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=20,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels
                ),
                link=dict(
                    source=flows["source"],
                    target=flows["target"],
                    value=flows["count"]
                )
            )
        ]
    )

    fig.update_layout(
        title="Indicator Dissemination Profile per Algorithm",
        font_size=13
    )

    fig.show()

def plot_analysis(config,exp,data=None):
    #plot_average_source_score(config,exp)
    #plot_confidence_intervals_source_score(config,exp)
    plot_average_cumulative_reward(config,exp)
