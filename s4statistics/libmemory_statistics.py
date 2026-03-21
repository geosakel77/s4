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

import os
import pandas as pd
from pandas import DataFrame
import tracemalloc
from tracemalloc import Snapshot,Statistic
from typing import List
import seaborn as sns
import matplotlib.pyplot as plt

def get_memory_files(config,exp,file_type=".dat"):
    memory_files=[]
    for filename in os.listdir(str(os.path.join(config['experiment_results_path'],exp))):
        if filename.endswith(file_type):
            memory_files.append(filename)
    return memory_files



def load_memory_file(config,exp, filename)->Snapshot:
    snapshot=Snapshot.load(str(os.path.join(config['experiment_results_path'],exp,filename)))
    return snapshot

def load_csv_file(config,exp, filename)->DataFrame:
    df= pd.read_csv(str(os.path.join(config['experiment_results_path'],exp,filename)))
    df=df[df["file"].str.contains("s4")]
    df=df[~df["file"].str.contains("venv")]
    df=df[~df["file"].str.contains("templates|s4config|libbase|libapiserver|experiments|utils|utlis",na=False)]
    df.loc[df["file"].str.contains("src",na=False),"file"]="SRC"
    df.loc[df["file"].str.contains("libapiclient.py", na=False), "file"] = "SRC"
    df.loc[df["file"].str.contains("rlagent", na=False), "file"] = "RL Agent"
    df.loc[df["file"].str.contains("qlearning|expectedsarsa|actorcritic", na=False), "file"] = "RL Algorithm"
    df.loc[df["file"].str.contains("ia.py", na=False), "file"] = "IA"
    df.loc[df["file"].str.contains("agcti.py", na=False), "file"] = "AgCTI"
    df.loc[df["file"].str.contains("dm.py", na=False), "file"] = "DM"
    df.loc[df["file"].str.contains("ta.py", na=False), "file"] = "TA"
    df.loc[df["file"].str.contains("is.py", na=False), "file"] = "AgCTI"
    df.loc[df["file"].str.contains("environment.py", na=False), "file"] = "RL Environment"

    df1=df.groupby(["timestamp","file"])[["memory_mb","alloc_count"]].sum().reset_index()
    return df1






def analyze_snapshot(snapshot:Snapshot,config)->None:
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    lineno_statistics= filter_statistics(snapshot,'lineno')
    print(lineno_statistics)
    traceback_statistics=filter_statistics(snapshot,'traceback')
    print(traceback_statistics)
    filename_statistics=filter_statistics(snapshot,'filename',cumulative=True)
    print(filename_statistics)
    display_top(filename_statistics, limit=0)
    display_tracebacks(traceback_statistics, limit=0)
    generate_flamegraph(traceback_statistics,config,exp="exp4")


def filter_statistics(snapshot:Snapshot,key_type='lineno',cumulative=False)->List[Statistic]:
    if not key_type=="traceback":
        stats = snapshot.statistics(key_type, cumulative=cumulative)
    else:
        stats = snapshot.statistics(key_type)
    s4_only_memory_stats=[]
    for stat in stats:
        frame = stat.traceback[0]
        if "s4" in frame.filename and ".venv" not in frame.filename:
            s4_only_memory_stats.append(stat)
    return s4_only_memory_stats

def display_top(statistics, key_type='lineno', limit=30):

    if limit ==0:
        limit = len(statistics)

    print("\n" + "="*70)
    print(f"Top {limit} allocations by {key_type}")
    print("="*70)
    for index, stat in enumerate(statistics[:limit], 1):
        frame = stat.traceback[0]
        size_mb = stat.size / (1024 * 1024)
        if 's4' in frame.filename:
            print(f"\n#{index}")
            print(f"{frame.filename}:{frame.lineno}")
            print(f"Memory: {size_mb:.5f} MB")
            print(f"Allocations: {stat.count}")
            line = frame.lineno
            if line:
                print(f"Code: {line}")
    
    total = sum(stat.size for stat in statistics)
    print("\nTotal allocated size: %.2f MB" % (total / (1024*1024)))


def display_tracebacks(statistics, limit=0):

    if limit ==0:
        limit = len(statistics)

    print("\n" + "="*70)
    print(f"Top {limit} allocation tracebacks")
    print("="*70)
    for stat in statistics:
        print("\nMemory: %.5f MB  Allocations: %d"
              % (stat.size / (1024*1024), stat.count))

        for frame in stat.traceback.format():
            print(frame)


def generate_flamegraph(statistics, config,exp="exp4",filename="stats_0.folded"):
    filename=os.path.join(config['images_path'],"plots",exp,filename)
    with open(filename,'w',encoding="utf-8") as f:
        for stat in statistics:
            stack=[]
            for frame in stat.traceback:
                stack.append(f"{frame.filename}:{frame.lineno}")
            folded_stack = ";".join(stack)
            f.write(f"{folded_stack} {stat.size}\n")


def generate_memory_utilization_over_time(df:DataFrame,filename)->None:
    plot_df = df.copy()

    plot_df["time_delta_sec"] = (
            plot_df["timestamp"] - plot_df["timestamp"].min()
    )

    plot_df["memory_mb"] =plot_df["memory_mb"]/(1024*1024)

    print(plot_df.head(10))

    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=plot_df,
        x="time_delta_sec",
        y="memory_mb",
        hue="file",
        marker="o"
    )

    plt.xlabel("Time (Sec)")
    plt.ylabel("Memory (MB)")
    plt.xticks(rotation=45)
    plt.legend(title="Objects", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def generate_memory_allocation_count_over_time(df:DataFrame,filename)->None:
    plot_df = df.copy()

    plot_df["time_delta_sec"] = (
            plot_df["timestamp"] - plot_df["timestamp"].min()
    )
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=plot_df,
        x="time_delta_sec",
        y="alloc_count",
        hue="file",
        marker="o"
    )

    plt.xlabel("Time (Sec)")
    plt.ylabel("Alloc Count")
    plt.xticks(rotation=45)
    plt.legend(title="Objects", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()



