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

from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
from s4statistics.s6lib.s6libstatistics import prepare_source_score_data,prepare_agent_data,prepare_validation_data,plot_exp_analysis

EXP=["exp1","exp2","exp3","exp4","exp5"]


def prepare_source_data_df(config):
    for exp in EXP:
        print(f"Preparing source data for {exp}")
        prepare_source_score_data(config,exp)

def prepare_agents_data_df(config):
    for exp in EXP:
        print(f"Preparing agents data for {exp}")
        prepare_agent_data(config,exp)

def prepare_data(config):
    prepare_validation_data(config)
    prepare_agents_data_df(config)
    prepare_source_data_df(config)

def plot_experiments_analysis(config):
    for exp in EXP:
        plot_exp_analysis(config,exp)


def run():
    config = read_config(CONFIG_PATH)
    #prepare_data(config)
    plot_experiments_analysis(config)

if __name__ == '__main__':
    run()