from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
import pandas as pd
from s4statistics.s6libds.s6dsanalysis import TADatasetCreator, CTIPoolDatasetCreator, network_analysis, \
    structural_overview, cardinality_distribution_analyze, relationship_analyze, cardinality_distribution_analyze_cti


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



if __name__ == '__main__':
    config = read_config(CONFIG_PATH)
    create_ta_dataset(config)
    create_cti_pool_dataset(config)
    analyze_ta_dataset()
    analyze_cti_pool_dataset()
