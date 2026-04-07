from s4reward.librewardanalysis import run_experiments,reward_function,summarize_experiments,plot_parameter_effects,plot_pairwise_heatmap,plot_runtime_analysis
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
import os






if __name__ == "__main__":
    config_data = read_config(CONFIG_PATH)
    param_grid = {
        "l1": [0.1, 0.2,0.3,0.4,0.5, 0.6, 0.7, 0.8, 0.9,1.0],
        "l2": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "l3": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "hit_reward": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "hit_status": [True,False],
        "appl_reward": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "appl_status": [True, False],
        "is_num": [5,10,15,20],
        "info_assets_num": [10, 20, 30, 40],
    }

    df_raw = run_experiments(
        func=reward_function,
        param_grid=param_grid,
        repetitions=10,
        base_seed=123,
        seed_param_name="seed",
    )

    df_summary = summarize_experiments(df_raw, metric_column="output")

    print("RAW RESULTS")
    print(df_raw.head(), end="\n\n")

    print("SUMMARY")
    print(df_summary.head(10), end="\n\n")

    os.makedirs(os.path.join(config_data['experiment_results_path'], "reward_analysis"), exist_ok=True)

    df_raw_csv = "df_raw.csv"
    df_raw_csv_file_path = os.path.join(config_data['experiment_results_path'], "reward_analysis", df_raw_csv)
    df_raw.to_csv(df_raw_csv_file_path, index=False)
    df_summary_csv = "df_summary.csv"
    df_summary_csv_file_path = os.path.join(config_data['experiment_results_path'], "reward_analysis", df_summary_csv)
    df_summary.to_csv(df_summary_csv_file_path, index=False)

    os.makedirs(os.path.join(config_data['images_path'], "plots","reward_analysis"), exist_ok=True)
    images_path=os.path.join(config_data['images_path'], "plots","reward_analysis")
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
        parameter_names=["hit_reward","appl_reward"],
        metric_mean_col="output_mean",
        metric_std_col="output_std",
        save_prefix="plot",
        file_path=images_path,
    )


    plot_parameter_effects(
        summary_df=df_summary,
        parameter_names=["info_assets_num","is_num"],
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
        save_path=os.path.join(images_path,"heatmap_hti_reward_appl_reward.png"),
    )

    plot_pairwise_heatmap(
        summary_df=df_summary,
        param_x="info_assets_num",
        param_y="is_num",
        metric_mean_col="output_mean",
        save_path=os.path.join(images_path,"heatmap_info_assets_num_is_num.png"),
    )

    # Plot runtime effect
    plot_runtime_analysis(
        summary_df=df_summary,
        parameter_name="hit_reward",
        runtime_col="runtime_sec_mean",
        save_path=os.path.join(images_path,"runtime_hit_reward.png"),
    )
