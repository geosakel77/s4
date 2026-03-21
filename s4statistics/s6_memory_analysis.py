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

from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
from s4statistics.libmemory_statistics import get_memory_files, generate_memory_allocation_count_over_time,load_csv_file,generate_memory_utilization_over_time
import os

def process_csv(config,exp):
    memory_files = get_memory_files(config, exp, file_type=".csv")
    for memory_file in memory_files:
        df=load_csv_file(config, exp, memory_file)
        os.makedirs(os.path.join(config['images_path'], "plots", exp),exist_ok=True)
        plot_filename = os.path.join(config['images_path'], "plots", exp, memory_file.split(".")[0]+".png")
        generate_memory_utilization_over_time(df,str(plot_filename))
        plot_filename_1 = os.path.join(config['images_path'], "plots", exp, memory_file.split(".")[0] + "alloc_count.png")
        generate_memory_allocation_count_over_time(df,str(plot_filename_1))

if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    exp="exp5"
    process_csv(config,exp)
    #memory_files=get_memory_files(config,exp,file_type=".csv")
    #for memory_file in memory_files:
    #    snapshot=load_memory_file(config,exp,memory_file)
    #    analyze_snapshot(snapshot,config)
    #    break