from SALib.sample import saltelli

from s4reward.librewardplots import plot_parameter_effects,plot_pairwise_heatmap,plot_runtime_analysis,plot_sobol_analysis,plot_reward_surface
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
import os
import pandas as pd
from s4reward.librewardanalysis import analyze_sobol
import numpy as np
from sklearn.ensemble import RandomForestRegressor

ANALYSIS_CODE = "A4"

def main1(df_raw,df_summary):
    saltelli_problem = {
        'num_vars': 3,
        'names': ['l1', 'l2', 'l3'],
        'bounds': [
            [df_raw['l1'].min(), df_raw['l1'].max()],
            [df_raw['l2'].min(), df_raw['l2'].max()],
            [df_raw['l3'].min(), df_raw['l3'].max()]
        ]
    }
    sobol_df, S2 = analyze_sobol(df_raw, parameter_names=["l1", 'l2', "l3"],saltelli_problem=saltelli_problem)
    os.makedirs(os.path.join(config_data['experiment_results_path'], "reward_analysis"), exist_ok=True)

    os.makedirs(os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE), exist_ok=True)
    images_path = os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE)

    parameters_name = ["l1", "l2", "l3"]

    plot_sobol_analysis(sobol_df=sobol_df, S2=S2, parameter_names=["l1", "l2", "l3"], save_prefix="plot",
                        file_path=images_path)

    # Plot single-parameter effects
    plot_parameter_effects(
        summary_df=df_summary,
        parameter_names=["l1", "l2", "l2"],
        metric_mean_col="output_mean",
        metric_std_col="output_std",
        save_prefix="plot",
        file_path=images_path,
    )
    plot_parameter_effects(
        summary_df=df_summary,
        parameter_names=["hit_reward", "appl_reward"],
        metric_mean_col="output_mean",
        metric_std_col="output_std",
        save_prefix="plot",
        file_path=images_path,
    )

    plot_parameter_effects(
        summary_df=df_summary,
        parameter_names=["info_assets_num", "is_num"],
        metric_mean_col="output_mean",
        metric_std_col="output_std",
        save_prefix="plot",
        file_path=images_path,
    )

    # Plot pairwise interaction
    plot_pairwise_heatmap(
        summary_df=df_summary,
        param_x="hit_reward",
        param_y="appl_reward",
        metric_mean_col="output_mean",
        save_path=os.path.join(images_path, "heatmap_hti_reward_appl_reward.png"),
    )

    plot_pairwise_heatmap(
        summary_df=df_summary,
        param_x="info_assets_num",
        param_y="is_num",
        metric_mean_col="output_mean",
        save_path=os.path.join(images_path, "heatmap_info_assets_num_is_num.png"),
    )

    # Plot runtime effect
    plot_runtime_analysis(
        summary_df=df_summary,
        parameter_name="hit_reward",
        runtime_col="runtime_sec_mean",
        save_path=os.path.join(images_path, "runtime_hit_reward.png"),
    )

def main2(df_s):
    saltelli_problem = {
        'num_vars': 3,
        'names': ['v1', 'v2', 'v3'],
        'bounds': [
            [df_s['v1'].min(), df_s['v1'].max()],
            [df_s['v2'].min(), df_s['v2'].max()],
            [df_s['v3'].min(), df_s['v3'].max()]
        ]
    }
    sobol_df, S2 = analyze_sobol(df_s, parameter_names=["v1", 'v2', "v3"],saltelli_problem=saltelli_problem,y_col="reward")
    os.makedirs(os.path.join(config_data['experiment_results_path'], "reward_analysis"), exist_ok=True)

    os.makedirs(os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE), exist_ok=True)
    images_path = os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE)

    parameters_name = ["l1", "l2", "l3"]

    plot_sobol_analysis(sobol_df=sobol_df, S2=S2, parameter_names=["v1", "v2", "v3"], save_prefix="plot",
                        file_path=images_path)

def main3(df_v3):
    saltelli_problem = {
        'num_vars': 2,
        'names': ['is_num', 'is_assets_num'],
        'bounds': [
            [df_v3['is_num'].min(), df_v3['is_num'].max()],
            [df_v3['is_assets_num'].min(), df_v3['is_assets_num'].max()]
        ]
    }
    sobol_df, S2 = analyze_sobol(df_v3, parameter_names=["is_num", 'is_assets_num'],saltelli_problem=saltelli_problem,y_col="v3")
    os.makedirs(os.path.join(config_data['experiment_results_path'], "reward_analysis"), exist_ok=True)

    os.makedirs(os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE), exist_ok=True)
    images_path = os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE)


    plot_sobol_analysis(sobol_df=sobol_df, S2=S2, parameter_names=["is_num", "is_assets_num"], save_prefix="plot",
                        file_path=images_path)

def main4(df_r):
    output_col="reward"
    df_r_sample=df_r.sample(n=60000000,random_state=42)
    X=df_r_sample[["v1+v2","v3"]]
    y=df_r_sample[output_col]
    model = RandomForestRegressor(n_estimators=100, random_state=42,max_depth=10,min_samples_leaf=100)
    model.fit(X, y)
    v1v2_range=np.linspace(df_r['v1+v2'].min(), df_r['v1+v2'].max(), 100)
    v3_range =np.linspace(df_r['v3'].min(), df_r['v3'].max(), 100)
    L1, L2 =np.meshgrid(v1v2_range, v3_range)

    grid_points=np.c_[L1.ravel(), L2.ravel()]
    grid_points_df = pd.DataFrame(grid_points, columns=["v1+v2", "v3"])
    Z=model.predict(grid_points_df)
    Z=Z.reshape(L1.shape)

    os.makedirs(os.path.join(config_data['experiment_results_path'], "reward_analysis"), exist_ok=True)

    os.makedirs(os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE), exist_ok=True)
    images_path = os.path.join(config_data['images_path'], "plots", "reward_analysis", ANALYSIS_CODE)
    plot_reward_surface(L1=L1, L2=L2, Z=Z, save_prefix="plot",file_path=images_path)


if __name__ == "__main__":
    config_data = read_config(CONFIG_PATH)
    df_raw_csv = "raw_experiments.csv"
    df_raw_csv_file_path = os.path.join(config_data['experiment_results_path'], "reward_analysis", df_raw_csv)
    df_raw =pd.read_csv(df_raw_csv_file_path)
    df_summary_csv = "df_summary.csv"
    df_summary_csv_file_path = os.path.join(config_data['experiment_results_path'], "reward_analysis", df_summary_csv)
    df_summary =pd.read_csv(df_summary_csv_file_path)
    print(df_raw.columns, end="\n\n")
    df_s=pd.DataFrame({
        "v1":df_raw['l1']*df_raw['hit_reward'],
        "v2":df_raw['l2']*df_raw['appl_reward'],
        "v3":df_raw['output']-df_raw['l1']*df_raw['hit_reward']-df_raw['l2']*df_raw['appl_reward'],
        "reward":df_raw["output"]
    })

    df_v3 = pd.DataFrame({
        "is_num":df_raw['is_num'],
        "is_assets_num":df_raw['info_assets_num'],
        "v3":df_raw['output']-df_raw['l1']*df_raw['hit_reward']-df_raw['l2']*df_raw['appl_reward'],
    })

    df_r= pd.DataFrame({
        "v1+v2": df_raw['l1'] * df_raw['hit_reward']+df_raw['l2'] * df_raw['appl_reward'],
        "v3": df_raw['output'] - df_raw['l1'] * df_raw['hit_reward'] - df_raw['l2'] * df_raw['appl_reward'],
        "reward": df_raw["output"]
    })

    print("RAW RESULTS")
    print(df_raw.head(), end="\n\n")


    print("SUMMARY")
    print(df_summary.head(10), end="\n\n")
    print("V3_REWARD")
    print(df_r.head(10), end="\n\n")
    #main1(df_raw,df_summary)

    main2(df_s)
    main3(df_v3)
    main4(df_r)

