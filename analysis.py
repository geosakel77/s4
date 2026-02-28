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

from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
from s4statistics.libstatistics import prepare_source_score_data,source_score_matrix_plot,prepare_agents_data,agents_data_plots,plot_source_score_matrix_comparison_all,plot_cumulative_reward_all_types, plot_cumulative_decisions


def run():
    config = read_config(CONFIG_PATH)
    source_score_df_data=prepare_source_score_data(config)
    #source_score_matrix_plot(source_score_df_data, config)
    agents_data=prepare_agents_data(config)
    #agents_data_plots(agents_data,config)
    #plot_source_score_matrix_comparison_all(source_score_df_data, config)
    #plot_cumulative_reward_all_types(agents_data,config)
    plot_cumulative_decisions(agents_data,config)

if __name__ == '__main__':
    run()
