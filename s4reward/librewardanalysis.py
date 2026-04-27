from __future__ import annotations
from SALib.analyze import sobol
import itertools
import inspect
import random
import time
from typing import Any, Callable
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from SALib.sample import saltelli

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

def analyze_sobol(
    df: pd.DataFrame,
    parameter_names: list,
    saltelli_problem: dict,
y_col:str="output"
)-> tuple[pd.DataFrame, pd.DataFrame]:
    df_sample=df.sample(n=60000000,random_state=42)
    X=df_sample[parameter_names]
    y=df_sample[y_col]
    model = RandomForestRegressor(n_estimators=100, random_state=42,max_depth=10,min_samples_leaf=100)
    model.fit(X,y)
    problem = saltelli_problem
    param_values = saltelli.sample(
        problem,
        1024,
        calc_second_order=True
    )
    Y = model.predict(param_values)

    Si = sobol.analyze(
        problem,
        Y,
        calc_second_order=True,
        print_to_console=True
    )
    sobol_df = pd.DataFrame({
        'parameter': problem['names'],
        'S1_first_order': Si['S1'],
        'S1_conf': Si['S1_conf'],
        'ST_total_order': Si['ST'],
        'ST_conf': Si['ST_conf']
    })

    S2 = pd.DataFrame(Si['S2'],index=problem['names'],columns=problem['names'])

    return sobol_df,S2
