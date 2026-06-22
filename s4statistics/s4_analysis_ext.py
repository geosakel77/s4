"""
Qualitative Assessment and Application of CTI based on Reinforcement Learning.
    Copyright (C) 2026  Georgios Sakellariou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from distutils.command.config import config

import pandas as pd
import os
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
from s4statistics.s6lib.s6libstatistics import prepare_source_score_data,prepare_agent_data,prepare_validation_data,plot_exp_analysis
from s4statistics.libstatisticsext import plot_analysis,plot_comparison,plot_average_actionability
from experiments.s4_exp_ext import load_data
EXP=["expa0","expa1","expa2","expa3","expa4","expa5","expa6","expa7","expa8","expa9"]


def prepare_source_data_df(config):
    for exp in EXP:
        print(f"Preparing source data for {exp}")
        prepare_source_score_data(config,exp)

def prepare_agents_data_df(config):
    for exp in EXP:
        print(f"Preparing agents data for {exp}")
        prepare_agent_data(config,exp)

def prepare_data(config):
    prepare_agents_data_df(config)
    prepare_source_data_df(config)

def plot_experiments_analysis(config):
    data=pd.read_csv(os.path.join(config['experiment_results_path'], "agents_data", f"exp0_comp_decided_actions.csv"))
    plot_comparison(config,data)
    #plot_analysis(config,EXP)

def run():
    config = read_config(CONFIG_PATH)
    #prepare_data(config)
    #plot_experiments_analysis(config)
    df=load_data(config)
    plot_average_actionability(config,df)

if __name__ == '__main__':
    run()