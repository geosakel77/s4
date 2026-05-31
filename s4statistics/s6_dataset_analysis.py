from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
import pandas as pd
from s4statistics.s6libds.s6dsanalysis import TADatasetCreator, CTIPoolDatasetCreator, network_analysis, \
    structural_overview, cardinality_distribution_analyze, relationship_analyze, cardinality_distribution_analyze_cti, \
    plot_compare_sets, plot_compare_sets_v1


def create_ta_dataset(config_data):
    ta_dataset_creator = TADatasetCreator(config_data)
    ta_dataset_df = ta_dataset_creator.get_dataset()
    ta_dataset_df.to_csv("ta_dataset_df.csv")


def create_cti_pool_dataset(config_data):
    cti_pool_dataset_creator = CTIPoolDatasetCreator(config_data)
    cti_pool_dataset_df = cti_pool_dataset_creator.get_cti_pool_dataset_df()
    cti_pool_dataset_df.to_csv("cti_pool_dataset_df.csv")


def analyze_ta_dataset():
    dataset = pd.read_csv("ta_dataset_df.csv")
    structural_overview(dataset)
    relationship_analyze(dataset)
    network_analysis(dataset)
    dataset = dataset.drop(columns=['no'])
    cardinality_distribution_analyze(dataset)


def analyze_cti_pool_dataset():
    dataset = pd.read_csv("cti_pool_dataset_df.csv")
    structural_overview(dataset)
    dataset = dataset.drop(columns=['no'])
    cardinality_distribution_analyze_cti(dataset)


def compare_datasets():
    ta_dataset = pd.read_csv("ta_dataset_df.csv")
    cti_pool_dataset = pd.read_csv("cti_pool_dataset_df.csv")
    set_ta_dataset = set(ta_dataset['indicator_id'].dropna())
    set_cti_pool_dataset = set(cti_pool_dataset['ind_id'].dropna())
    print("Actor set size:", len(set_ta_dataset))
    print("Indicator set size:", len(set_cti_pool_dataset))
    print("Intersection:", len(set_ta_dataset & set_cti_pool_dataset))
    only_ta_dataset = len(set_ta_dataset - set_cti_pool_dataset)
    only_cti_pool_dataset = len(set_cti_pool_dataset - set_ta_dataset)
    both = len(set_ta_dataset & set_cti_pool_dataset)

    total = len(set_ta_dataset | set_cti_pool_dataset)

    print(f"Only TA Dataset: {only_ta_dataset} ({only_ta_dataset / total:.2%})")
    print(f"Only CTI Pool Dataset: {only_cti_pool_dataset} ({only_cti_pool_dataset / total:.2%})")
    print(f"Overlap: {both} ({both / total:.2%})")
    plot_compare_sets(set_ta_dataset, set_cti_pool_dataset)
    plot_compare_sets_v1(set_ta_dataset, set_cti_pool_dataset)

if __name__ == '__main__':
    config = read_config(CONFIG_PATH)
    #create_ta_dataset(config)
    #create_cti_pool_dataset(config)
    #analyze_ta_dataset()
    #analyze_cti_pool_dataset()
    compare_datasets()
