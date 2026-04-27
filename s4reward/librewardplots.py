import matplotlib.pyplot as plt
import os
import pandas as pd

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

def plot_sobol_analysis(
    sobol_df: pd.DataFrame,
        S2: pd.DataFrame,
    parameter_names: list[str],
    save_prefix: str | None = None,
    file_path: str | None = None,
) -> None:
    """
    Plot sobol sensitivity analysis.
    """
    sobol_df.plot(
        x='parameter',
        y=['S1_first_order', 'ST_total_order'],
        kind='bar',
        figsize=(8, 5)
    )

    plt.ylabel('Sensitivity Index (Sobol)')
    plt.title(f'Sensitivity Analysis for Reward (Sobol)')
    plt.xticks(rotation=0)
    plt.grid(axis='y')
    plt.tight_layout()
    if save_prefix:
        file_name=f"{save_prefix}_first_order_total_order_{'_'.join(parameter_names)}.png"
        file_name_path = os.path.join(file_path, file_name)
        plt.savefig(file_name_path, dpi=200)

    plt.show()
    plt.figure(figsize=(6, 5))
    plt.imshow(S2, interpolation='nearest')
    plt.colorbar(label='Second-Order Index (Sobol)')
    plt.xticks(range(len(parameter_names)), parameter_names)
    plt.yticks(range(len(parameter_names)), parameter_names)
    plt.title(f'Second-Order Interaction Effects for Reward')
    plt.tight_layout()
    if save_prefix:
        file_name_1=f"{save_prefix}_second_order_{'_'.join(parameter_names)}.png"
        file_name_path_1 = os.path.join(file_path, file_name_1)
        plt.savefig(file_name_path_1, dpi=200)
    plt.show()

    def plot_sobol_analysis(
            sobol_df: pd.DataFrame,
            S2: pd.DataFrame,
            parameter_names: list[str],
            save_prefix: str | None = None,
            file_path: str | None = None,
    ) -> None:
        """
        Plot sobol sensitivity analysis.
        """
        sobol_df.plot(
            x='Parameter',
            y=['S1_first_order', 'ST_total_order'],
            kind='bar',
            figsize=(8, 5)
        )

        plt.ylabel('Sensitivity Index (Sobol)')
        plt.title(f'Sensitivity Analysis for Reward (Sobol)')
        plt.xticks(rotation=0)
        plt.grid(axis='y')
        plt.tight_layout()
        if save_prefix:
            file_name = f"{save_prefix}_first_order_total_order_{'_'.join(parameter_names)}.png"
            file_name_path = os.path.join(file_path, file_name)
            plt.savefig(file_name_path, dpi=200)

        plt.show()
        plt.figure(figsize=(6, 5))
        plt.imshow(S2, interpolation='nearest')
        plt.colorbar(label='Second-Order Index (Sobol)')
        plt.xticks(range(len(parameter_names)), parameter_names)
        plt.yticks(range(len(parameter_names)), parameter_names)
        plt.title(f'Second-Order Interaction Effects for Reward')
        plt.tight_layout()
        if save_prefix:
            file_name_1 = f"{save_prefix}_second_order_{'_'.join(parameter_names)}.png"
            file_name_path_1 = os.path.join(file_path, file_name_1)
            plt.savefig(file_name_path_1, dpi=200)
        plt.show()

def plot_reward_surface(L1,L2,Z, save_prefix: str | None = None,file_path: str | None = None,
) -> None:
    """
    Plot reward surface.
    """
    fig =plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111,projection='3d')
    surf = ax.plot_surface(L1,L2,Z)

    ax.set_xlabel('v1+v2')
    ax.set_ylabel('v3')
    ax.set_zlabel('reward')
    ax.set_title('Reward=v1+v2+v3')
    fig.colorbar(surf, shrink=0.5, aspect=10)
    plt.tight_layout()
    if save_prefix:
        file_name=f"{save_prefix}_reward_v1v2v3.png"
        file_name_path = os.path.join(file_path, file_name)
        plt.savefig(file_name_path, dpi=200)
    plt.show()