from __future__ import annotations

import itertools
import inspect
import random
import time,os
from typing import Any, Callable

import matplotlib.pyplot as plt
import pandas as pd


def run_experiments(
    func: Callable[..., Any],
    param_grid: dict[str, list[Any]],
    repetitions: int = 1,
    base_seed: int = 42,
    seed_param_name: str | None = "seed",
) -> pd.DataFrame:
    """
    Run experiments for all parameter combinations of a function.
    """
    if not param_grid:
        raise ValueError("param_grid cannot be empty.")

    func_signature = inspect.signature(func)
    func_params = set(func_signature.parameters.keys())

    invalid_params = [p for p in param_grid if p not in func_params]
    if invalid_params:
        raise ValueError(f"These parameters are not in the function signature: {invalid_params}")

    keys = list(param_grid.keys())
    combinations = list(itertools.product(*(param_grid[k] for k in keys)))

    results: list[dict[str, Any]] = []

    for combo_idx, combo in enumerate(combinations):
        param_values = dict(zip(keys, combo))
        print(combo_idx)
        for repetition in range(repetitions):
            call_params = param_values.copy()

            seed = base_seed + combo_idx * 1000 + repetition
            if seed_param_name and seed_param_name in func_params:
                call_params[seed_param_name] = seed

            start = time.perf_counter()

            try:
                output = func(**call_params)
                error = None
                success = True
            except Exception as exc:
                output = None
                error = str(exc)
                success = False

            runtime_sec = time.perf_counter() - start

            row = {
                **param_values,
                "repetition": repetition,
                "success": success,
                "output": output,
                "error": error,
                "runtime_sec": runtime_sec,
            }

            if seed_param_name and seed_param_name in func_params:
                row["seed"] = seed

            results.append(row)

    return pd.DataFrame(results)


def summarize_experiments(
    df: pd.DataFrame,
    metric_column: str = "output",
    success_only: bool = True,
) -> pd.DataFrame:
    """
    Summarize experiment results by parameter combination.
    """
    if metric_column not in df.columns:
        raise ValueError(f"Column '{metric_column}' not found in dataframe.")

    summary_df = df.copy()

    if success_only and "success" in summary_df.columns:
        summary_df = summary_df[summary_df["success"] == True].copy()

    excluded_cols = {"repetition", "seed", "success", "output", "error", "runtime_sec"}
    group_cols = [c for c in summary_df.columns if c not in excluded_cols]

    if not group_cols:
        raise ValueError("No parameter columns found for grouping.")

    agg_dict = {
        metric_column: ["mean", "std", "min", "max", "count"],
        "runtime_sec": ["mean", "std", "min", "max"],
    }

    summary = summary_df.groupby(group_cols).agg(agg_dict)
    summary.columns = ["_".join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    if f"{metric_column}_mean" in summary.columns:
        summary = summary.sort_values(by=f"{metric_column}_mean", ascending=False)

    return summary


def plot_parameter_effects(
    summary_df: pd.DataFrame,
    parameter_names: list[str],
    metric_mean_col: str = "output_mean",
    metric_std_col: str = "output_std",
    save_prefix: str | None = None,
    file_path: str | None = None,
) -> None:
    """
    Plot average effect of each parameter on the output metric.
    """
    for parameter_name in parameter_names:
        effect_df = (
            summary_df.groupby(parameter_name, as_index=False)
            .agg(
                avg_metric=(metric_mean_col, "mean"),
                std_metric=(metric_mean_col, "std"),
            )
            .sort_values(by=parameter_name)
        )

        plt.figure(figsize=(8, 5))
        plt.errorbar(
            effect_df[parameter_name],
            effect_df["avg_metric"],
            yerr=effect_df["std_metric"],
            marker="o",
            capsize=4,
        )
        plt.xlabel(parameter_name)
        plt.ylabel(metric_mean_col)
        plt.title(f"Effect of {parameter_name} on {metric_mean_col}")
        plt.grid(True)
        plt.tight_layout()

        if save_prefix:
            file_name_path=os.path.join(file_path, f"{save_prefix}_{parameter_name}.png")
            plt.savefig(file_name_path, dpi=200)

        plt.show()


def plot_pairwise_heatmap(
    summary_df: pd.DataFrame,
    param_x: str,
    param_y: str,
    metric_mean_col: str = "output_mean",
    save_path: str | None = None,
) -> None:
    """
    Plot pairwise interaction heatmap for two parameters.
    Works best when both parameters have a manageable number of unique values.
    """
    heatmap_df = (
        summary_df.groupby([param_y, param_x], as_index=False)[metric_mean_col]
        .mean()
        .pivot(index=param_y, columns=param_x, values=metric_mean_col)
    )

    plt.figure(figsize=(8, 6))
    plt.imshow(heatmap_df, aspect="auto")
    plt.colorbar(label=metric_mean_col)
    plt.xticks(range(len(heatmap_df.columns)), heatmap_df.columns, rotation=45)
    plt.yticks(range(len(heatmap_df.index)), heatmap_df.index)
    plt.xlabel(param_x)
    plt.ylabel(param_y)
    plt.title(f"Heatmap of {metric_mean_col}: {param_y} vs {param_x}")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200)

    plt.show()


def plot_runtime_analysis(
    summary_df: pd.DataFrame,
    parameter_name: str,
    runtime_col: str = "runtime_sec_mean",
    save_path: str | None = None,
) -> None:
    """
    Plot runtime sensitivity for one parameter.
    """
    runtime_df = (
        summary_df.groupby(parameter_name, as_index=False)
        .agg(avg_runtime=(runtime_col, "mean"))
        .sort_values(by=parameter_name)
    )

    plt.figure(figsize=(8, 5))
    plt.plot(runtime_df[parameter_name], runtime_df["avg_runtime"], marker="o")
    plt.xlabel(parameter_name)
    plt.ylabel("Average runtime (sec)")
    plt.title(f"Runtime effect of {parameter_name}")
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200)

    plt.show()




# --------------------------------------------------
# Reward function
# --------------------------------------------------
def reward_function(l1: float,l2: float,l3: float, hit_reward: int, hit_status: bool,appl_reward: int, appl_status: bool, is_num: int, info_assets_num: int, seed: int | None = None) -> float:
    rng = random.Random(seed)
    if hit_status:
        h_r=hit_reward
    else:
        h_r=0
    if appl_status:
        a_r=appl_reward
    else:
        a_r=0
    r_dmx=0
    for i in range(is_num):
        v_1=rng.choice([-1,1])
        v_2a=rng.choice([1,2,3,4,5])
        v_2b=rng.choice([1,2,3])*rng.choice([1,2,3])*rng.choice([1,2,3])
        v_2=v_2a*v_2b
        v_is=0
        for j in range(info_assets_num):
            v_is=v_is+rng.choice([1,2,3,4,5])*asset_value(seed)
        r_dmx=r_dmx+v_1*v_2*v_is

    reward = l1*h_r+l2*a_r+l3*r_dmx
    return reward

def asset_value(seed):
    rng = random.Random(seed)
    rangeA=[1,2,3]
    return rng.choice(rangeA)+rng.choice(rangeA)+rng.choice(rangeA)
