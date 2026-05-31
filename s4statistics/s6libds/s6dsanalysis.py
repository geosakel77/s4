import os,json
import networkx as nx
from s4config.libconstants import MAP_TECHNIQUES_TO_TACTICS, EXPERIMENTS_ACTORS
import pandas as pd
from s4lib.libbase import read_from_json
from s4lib.libsrc import _set_cti_confidence,_set_indicator_types
from s4lib.libdm import Record
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib_venn import venn2
sns.set_style("darkgrid")

def get_pattern_types(experiments_data_path):
    file_paths = os.listdir(experiments_data_path)
    indicators={}
    actors={}
    techniques = {}
    for file_path in file_paths:
        with open(os.path.join(experiments_data_path, file_path), 'r', encoding='utf-8') as f:
            data = json.load(f)
            indicators[data['actor']['id']]=data['indicators']
            actors[data['actor']['id']]=data['actor']['name']
            techniques[data['actor']['id']]=data['techniques']
    pure_indicators = {}
    pattern_types_available = {}
    indicator_per_pattern_type = {}
    for ta_key, ta_indicators in indicators.items():
        pure_indicators[ta_key] = []
        pattern_types_available[ta_key] = []
        for bundle_key in ta_indicators.keys():
            for bundle in ta_indicators[bundle_key]:
                if bundle:
                    for indicator in bundle['objects']:
                        pure_indicators[ta_key].append(indicator)
                        if 'pattern' in indicator.keys():
                            v = indicator['pattern'].split(" ")[0].replace("[", "", 1).split(".")[0].replace("(", "")
                            if len(v)>3:
                                pattern_types_available[ta_key].append(v)
                                if v in indicator_per_pattern_type.keys():
                                    indicator_per_pattern_type[v].append(indicator['id'])
                                else:
                                    indicator_per_pattern_type[v] = [indicator['id']]
    return list(indicator_per_pattern_type.keys())

class TADatasetCreator:

    def __init__(self,ta_config):
        self.config = ta_config
        self.plan=None
        self.plan_indicators=None
        self.all_techniques=read_from_json(self.config['techniques_path'])
        self.actor_names=EXPERIMENTS_ACTORS
        self.pattern_types=get_pattern_types(self.config['experiments_data_path'])
        self.ta_dataset_df=self.create_all_plans()

    def get_dataset(self):
        return self.ta_dataset_df

    def create_all_plans(self):
        ta_dataset=[]
        for actor_name in self.actor_names:
            actor_id=self._initiate(actor_name=actor_name)
            plan,plan_indicators=self.create_plan()
            for key, value in plan_indicators.items():
                for indicator in value:
                    for ind_id,body in indicator.items():
                        pattern_type=None
                        for pt in self.pattern_types:
                            if pt in body['pattern']:
                                pattern_type=pt
                                break
                        for platform in body['platform']:
                            row={
                                "actor_id":actor_id,
                                "actor_name":actor_name,
                                'tactic':key,
                                "indicator_id":ind_id,
                                "pattern_type":pattern_type,
                                "pattern":body['pattern'],
                                "platform":platform,
                            }
                            ta_dataset.append(row)
        ta_dataset_df=pd.DataFrame(ta_dataset)
        return ta_dataset_df

    def _initiate(self,actor_name):
        actors = read_from_json(self.config['actors_path'])
        for key,value in actors.items():
            if value['name'] == actor_name:
                self.actor_id=key
        self.actor_name=actor_name
        self.actor_conf_file=f"{self.actor_id}.json"
        if os.path.exists(os.path.join(self.config['experiments_data_path'],self.actor_conf_file)):
            actors_config=read_from_json(os.path.join(self.config['experiments_data_path'],self.actor_conf_file))
            self.actor=actors_config['actor']
            self.actor_techniques=actors_config['techniques']
            self.actor_software=actors_config['software']
            self.actor_techniques_software_map=actors_config['actor_techniques_software_map']
            self.actor_techniques_to_tactics_map=actors_config['actor_techniques_to_tactics_map']
            self.indicators=actors_config['indicators']
        else:
            print("Error: Actor not found")
        return self.actor_id

    def _map_actor_techniques_to_software(self):
            actor_techniques_map={}
            actor_techniques_ids=[]
            actor_software_ids=[]
            for technique in self.actor_techniques:
               actor_techniques_ids.append(json.loads(technique['object'])['id'])
            for software in self.actor_software:
                actor_software_ids.append(json.loads(software['object'])['id'])
            software_using_technique=read_from_json(self.config['software_using_technique'])
            for technique_id in actor_techniques_ids:
                map_i=[]
                if technique_id in software_using_technique.keys():
                    software_obj_list = software_using_technique[technique_id]
                    for software_obj in software_obj_list:
                        software_id= json.loads(software_obj['object'])['id']
                        if software_id in actor_software_ids:
                            map_i.append(software_id)
                actor_techniques_map[technique_id] = map_i
            return actor_techniques_map

    def _map_actor_techniques_to_tactics(self):
        actor_techniques_to_tactics_map={}
        map_techniques_to_tactics= MAP_TECHNIQUES_TO_TACTICS
        for tactic in map_techniques_to_tactics.keys():
            list_of_techniques = []
            for technique in self.actor_techniques:
                technique_deserialized = json.loads(technique['object'])
                technique_external_id=technique_deserialized['external_references'][0]['external_id']
                if technique_deserialized['x_mitre_is_subtechnique']:
                    check_data= technique_external_id.split('.')[0]
                else:
                    check_data= technique_external_id
                if check_data in map_techniques_to_tactics[tactic]:
                    list_of_techniques.append(technique_deserialized['id'])
            if len(list_of_techniques)>0:
                actor_techniques_to_tactics_map[tactic] = list_of_techniques
        return actor_techniques_to_tactics_map

    def create_plan(self):
        plan={}
        plan_indicators={}
        for tactic in self.actor_techniques_to_tactics_map.keys():
            plan_techniques_of_tactic_n=self.actor_techniques_to_tactics_map[tactic]
            plan_soft_tools_of_tactic_n = {}
            if self.actor_techniques_software_map:
                for technique in plan_techniques_of_tactic_n:
                    sample_tools=self.actor_techniques_software_map[technique]
                    if len(sample_tools)>0:
                        plan_soft_tools_of_tactic_n[technique]=sample_tools
            plan[tactic]=(plan_techniques_of_tactic_n,plan_soft_tools_of_tactic_n)
        indicators = []
        if self.indicators:
            for ref in self.indicators[self.actor_id]:
                if ref:
                    for obj in ref['objects']:
                        if 'pattern' in obj.keys():
                            indicators.append({obj["id"]:{"pattern":obj['pattern'],"platform":["generic"]}})

        for tactic_n in plan.keys():
            plan_indicators[tactic_n]=[]
            if len(indicators)>0:
                indexes = sorted(range(len(indicators)), reverse=True)
                plan_indicators[tactic_n].extend([indicators.pop(i) for i in indexes])
            for technique, tool in plan[tactic_n][1].items():
                for tl in tool:
                    bundles=self.indicators[tl]
                    for bundle in bundles:
                        platform=[]
                        for obj in self.actor_techniques:
                            data = json.loads(obj['object'])
                            if technique == data['id']:
                                platform.extend(data['x_mitre_platforms'])
                        plan_indicators[tactic_n].extend([{indicator['id']:{"pattern":indicator['pattern'],"platform":platform}} for indicator in bundle['objects'] if 'pattern' in indicator.keys()])
        self.plan=plan
        self.plan_indicators=plan_indicators
        if (not self.plan) and indicators:
            #Special case that handles threat actors with no identified techniques or tactics which have indicators.
            plan_indicators["T000N"]=[]
            plan["T000N"]=(["TE000N"],{"TE000N":["TO000N"]})
            indexes = sorted(range(len(indicators)), reverse=True)
            plan_indicators["T000N"].extend([indicators.pop(i) for i in indexes])
        return plan,plan_indicators

class CTIPoolDatasetCreator:
    def __init__(self, config):
        self.config=config
        self.cti_data :dict[int,Record]= self._sample_cti_data()
        self.pattern_types = get_pattern_types(self.config['experiments_data_path'])
        self.cti_pool_dataset_df=self.create_cti_pool_dataset_df()

    def get_cti_pool_dataset_df(self):
        return self.cti_pool_dataset_df

    def _sample_cti_data(self):
        cti_sample_data = {}
        try:
            cti_data_pool=read_from_json(self.config['cti_data_pool'])
            selected_keys=list(cti_data_pool.keys())
            for key in selected_keys:
                if cti_data_pool[key]['type']=='indicator':
                    record_id = cti_data_pool[key]['id']
                    record_type = cti_data_pool[key]['type']
                    record_confidence = _set_cti_confidence(cti_data_pool[key])
                    record_indicator_type=_set_indicator_types(cti_data_pool[key])
                    value = cti_data_pool[key]['pattern'].replace("'",'').replace('"','')
                    new_record = Record(record_id, record_type, value,record_confidence,record_indicator_type)
                    cti_sample_data[key]=new_record
                elif cti_data_pool[key]['type']=='vulnerability':
                    record_id = cti_data_pool[key]['id']
                    record_type = cti_data_pool[key]['type']
                    value = cti_data_pool[key]['name'].replace("'",'').replace('"','')
                    record_confidence = _set_cti_confidence(cti_data_pool[key])
                    record_indicator_type=_set_indicator_types(cti_data_pool[key])
                    new_record = Record(record_id, record_type, value,record_confidence,record_indicator_type)
                    cti_sample_data[key]=new_record
        except Exception as e:
            print(e)
        return cti_sample_data

    def create_cti_pool_dataset_df(self):
        all_cti_data=[]
        for key, value in self.cti_data.items():
            for indicator_type in value.record_indicator_type:
                pattern_type=None
                for pt in self.pattern_types:
                    if pt in value.record_value:
                        pattern_type=pt
                row={"ind_id":value.record_id,
                     "type":value.record_type,
                    "pattern":value.record_value,
                     "confidence":value.record_confidence,
                     "indicator_type":indicator_type,
                     "pattern_type":pattern_type}
                all_cti_data.append(row)
        return pd.DataFrame(all_cti_data)


def structural_overview(df: pd.DataFrame):
    print("="*60)
    print("DATASET STRUCTURAL OVERVIEW")
    print("="*60)
    # 1. Shape
    print("\n[1] Dataset Shape")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # 2. Column Types
    print("\n[2] Column Data Types")
    print(df.dtypes)

    # 3. Missing Values
    print("\n[3] Missing Values Analysis")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100

    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct.round(2)
    }).sort_values(by='Missing Count', ascending=False)

    print(missing_df)

    # 4. Unique Values
    print("\n[4] Unique Values per Column")
    unique_vals = df.nunique()
    print(unique_vals)

    # 5. Duplicate Rows
    print("\n[5] Duplicate Rows")
    dup_count = df.duplicated().sum()
    print(f"Duplicate rows: {dup_count}")
    print(f"Duplicate %: {(dup_count/len(df))*100:.2f}%")

    # 6. Cardinality Insight
    print("\n[6] Cardinality Classification")
    for col in df.columns:
        uniq = df[col].nunique()
        if uniq == len(df):
            level = "High (Likely ID)"
        elif uniq > len(df)*0.5:
            level = "High"
        elif uniq > 10:
            level = "Medium"
        else:
            level = "Low"

        print(f"{col}: {uniq} unique values → {level}")

    # 7. Consistency Check (actor_id vs actor_name)
    print("\n[7] Consistency Check: actor_id ↔ actor_name")

    if 'actor_id' in df.columns and 'actor_name' in df.columns:
        mapping = df.groupby('actor_id')['actor_name'].nunique()
        inconsistent = mapping[mapping > 1]

        if len(inconsistent) == 0:
            print("✔ Each actor_id maps to a single actor_name (consistent)")
        else:
            print("⚠ Inconsistencies found:")
            print(inconsistent)

    # 8. Basic Memory Usage
    print("\n[8] Memory Usage")
    mem = df.memory_usage(deep=True).sum() / (1024**2)
    print(f"Total memory usage: {mem:.2f} MB")

    print("\n" + "="*60)


def cardinality_distribution_analysis(df:pd.DataFrame):
    print("="*60)
    print("CARDINALITY & DISTRIBUTION ANALYSIS")
    print("="*60)

    results = []

    for col in df.columns:
        total = len(df)
        unique = df[col].nunique()
        top_val = df[col].mode().iloc[0] if not df[col].mode().empty else None
        top_freq = df[col].value_counts().iloc[0] if not df[col].empty else 0

        results.append({
            "column": col,
            "unique_values": unique,
            "unique_ratio": round(unique / total, 4),
            "top_value": top_val,
            "top_frequency": top_freq,
            "top_ratio": round(top_freq / total, 4)
        })

    summary_df = pd.DataFrame(results).sort_values(by="unique_values", ascending=False)

    print("\n[1] Cardinality Summary")
    print(summary_df)

    print("\n[2] Distribution (Top Values per Column)")
    for col in df.columns:
        print(f"\n--- {col} ---")
        print(df[col].value_counts().head(10))

    return summary_df

def plot_top_categories(df, column, top_n=10):
    plt.figure(figsize=(8, 5))
    sns.countplot(
        y=column,
        data=df,
        order=df[column].value_counts().head(top_n).index
    )
    plt.title(f"Top {top_n} values of {column}")
    plt.tight_layout()
    plt.show()

def plot_cardinality(summary_df):
    plt.figure(figsize=(10, 5))
    sns.barplot(
        x="column",
        y="unique_values",
        data=summary_df
    )
    plt.xticks(rotation=45)
    plt.title("Cardinality per Column")
    plt.tight_layout()
    plt.show()

def plot_distribution_heatmap(df, col1, col2):
    cross = pd.crosstab(df[col1], df[col2])

    plt.figure(figsize=(10, 6))
    sns.heatmap(cross, cmap="viridis")
    plt.title(f"{col1} vs {col2}")
    plt.tight_layout()
    plt.show()

def cardinality_distribution_analyze(df:pd.DataFrame):
    # Run analysis
    summary = cardinality_distribution_analysis(df)

    # Plot examples
    plot_top_categories(df, 'actor_name')
    plot_top_categories(df, 'tactic')
    plot_top_categories(df, 'platform')

    plot_cardinality(summary)

    # Relationship view
    plot_distribution_heatmap(df, 'actor_name', 'tactic')

def cardinality_distribution_analyze_cti(df:pd.DataFrame):
    # Run analysis
    summary = cardinality_distribution_analysis(df)

    # Plot examples
    plot_top_categories(df, 'pattern')
    plot_top_categories(df, 'pattern_type')
    plot_top_categories(df, 'indicator_type')
    plot_top_categories(df, 'confidence')
    plot_top_categories(df, 'type')

    plot_cardinality(summary)

    # Relationship view
    plot_distribution_heatmap(df, 'pattern_type', 'indicator_type')
    plot_distribution_heatmap(df, 'pattern_type', 'confidence')

def relationship_analysis(df):
    print("="*70)
    print("RELATIONSHIP ANALYSIS / CROSS-DIMENSIONAL ANALYSIS")
    print("="*70)

    pairs = [
        ("actor_name", "tactic"),
        ("actor_name", "platform"),
        ("actor_name", "pattern_type"),
        ("tactic", "platform"),
        ("tactic", "pattern_type"),
        ("platform", "pattern_type")
    ]

    results = {}

    for col1, col2 in pairs:
        if col1 in df.columns and col2 in df.columns:
            print(f"\n[Relationship] {col1} ↔ {col2}")
            cross = pd.crosstab(df[col1], df[col2])
            print(cross)

            results[f"{col1}_vs_{col2}"] = cross

    return results

def plot_relationship_heatmap(df, col1, col2, top_n=20):
    """
    Creates a heatmap for two categorical columns.
    top_n limits the first dimension to avoid unreadable plots.
    """

    top_values = df[col1].value_counts().head(top_n).index
    filtered_df = df[df[col1].isin(top_values)]

    cross = pd.crosstab(filtered_df[col1], filtered_df[col2])

    plt.figure(figsize=(12, 7))
    sns.heatmap(cross, annot=True, fmt="d", cmap="Blues")

    plt.title(f"{col1} vs {col2}")
    plt.xlabel(col2)
    plt.ylabel(col1)
    plt.tight_layout()
    plt.show()

def actor_profile_analysis(df):
    """
    Summarizes each actor across tactics, platforms, indicators, and pattern types.
    """

    profile = df.groupby("actor_name").agg(
        records=("no", "count"),
        unique_actor_ids=("actor_id", "nunique"),
        unique_tactics=("tactic", "nunique"),
        unique_platforms=("platform", "nunique"),
        unique_indicators=("indicator_id", "nunique"),
        unique_pattern_types=("pattern_type", "nunique")
    ).reset_index()

    profile = profile.sort_values(by="records", ascending=False)

    print("="*70)
    print("ACTOR PROFILE SUMMARY")
    print("="*70)
    print(profile)

    return profile

def tactic_platform_matrix(df):
    """
    Shows how tactics are distributed across platforms.
    """

    matrix = pd.crosstab(df["tactic"], df["platform"])

    print("="*70)
    print("TACTIC ↔ PLATFORM MATRIX")
    print("="*70)
    print(matrix)

    return matrix

def normalized_crosstab(df, col1, col2):
    """
    Row-normalized crosstab.
    Shows percentages instead of raw counts.
    """

    table = pd.crosstab(df[col1], df[col2], normalize="index") * 100
    table = table.round(2)

    print(f"\nNormalized Relationship: {col1} ↔ {col2}")
    print(table)

    return table

def relationship_analyze(df:pd.DataFrame):
    # 1. Run all pairwise relationship tables
    relationship_results = relationship_analysis(df)

    # 2. Plot key relationships
    plot_relationship_heatmap(df, "actor_name", "tactic", top_n=20)
    plot_relationship_heatmap(df, "actor_name", "platform", top_n=20)
    plot_relationship_heatmap(df, "tactic", "platform", top_n=20)

    # 3. Actor-level behavioral profile
    actor_profiles = actor_profile_analysis(df)

    # 4. Tactic-platform matrix
    tp_matrix = tactic_platform_matrix(df)

    normalized_crosstab(df, "actor_name", "tactic")
    normalized_crosstab(df, "actor_name", "platform")
    normalized_crosstab(df, "tactic", "platform")

def build_cti_graph(df):
    G = nx.Graph()

    for _, row in df.iterrows():
        actor = f"actor:{row['actor_name']}"
        tactic = f"tactic:{row['tactic']}"
        indicator = f"indicator:{row['indicator_id']}"
        platform = f"platform:{row['platform']}"
        pattern_type = f"pattern_type:{row['pattern_type']}"

        G.add_node(actor, type="actor")
        G.add_node(tactic, type="tactic")
        G.add_node(indicator, type="indicator")
        G.add_node(platform, type="platform")
        G.add_node(pattern_type, type="pattern_type")

        G.add_edge(actor, tactic)
        G.add_edge(actor, indicator)
        G.add_edge(indicator, pattern_type)
        G.add_edge(tactic, platform)

    print("="*60)
    print("CTI GRAPH SUMMARY")
    print("="*60)
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Connected components: {nx.number_connected_components(G)}")

    return G

def graph_centrality_analysis(G, top_n=10):
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    centrality_df = pd.DataFrame({
        "node": list(G.nodes()),
        "type": [G.nodes[n].get("type") for n in G.nodes()],
        "degree_centrality": [degree_centrality[n] for n in G.nodes()],
        "betweenness_centrality": [betweenness_centrality[n] for n in G.nodes()],
        "closeness_centrality": [closeness_centrality[n] for n in G.nodes()]
    })

    centrality_df = centrality_df.sort_values(
        by="degree_centrality",
        ascending=False
    )

    print("="*60)
    print("TOP CENTRAL NODES")
    print("="*60)
    print(centrality_df.head(top_n))

    return centrality_df

def build_actor_indicator_graph(df):
    G_ai = nx.Graph()

    for _, row in df.iterrows():
        actor = f"actor:{row['actor_name']}"
        indicator = f"indicator:{row['indicator_id']}"

        G_ai.add_node(actor, type="actor")
        G_ai.add_node(indicator, type="indicator")
        G_ai.add_edge(actor, indicator)

    print("="*60)
    print("ACTOR ↔ INDICATOR GRAPH")
    print("="*60)
    print(f"Nodes: {G_ai.number_of_nodes()}")
    print(f"Edges: {G_ai.number_of_edges()}")

    return G_ai

def shared_indicators_between_actors(df):
    actor_indicators = (
        df.groupby("actor_name")["indicator_id"]
        .apply(set)
        .to_dict()
    )

    rows = []

    actors = list(actor_indicators.keys())

    for i in range(len(actors)):
        for j in range(i + 1, len(actors)):
            a1 = actors[i]
            a2 = actors[j]

            shared = actor_indicators[a1].intersection(actor_indicators[a2])

            if len(shared) > 0:
                rows.append({
                    "actor_1": a1,
                    "actor_2": a2,
                    "shared_indicators": len(shared),
                    "shared_indicator_ids": list(shared)
                })

    shared_df = pd.DataFrame(rows)

    if not shared_df.empty:
        shared_df = shared_df.sort_values(
            by="shared_indicators",
            ascending=False
        )

    print("="*60)
    print("SHARED INDICATORS BETWEEN ACTORS")
    print("="*60)
    print(shared_df)

    return shared_df

def plot_graph(G, max_nodes=100):
    if G.number_of_nodes() > max_nodes:
        nodes = list(G.nodes())[:max_nodes]
        H = G.subgraph(nodes)
    else:
        H = G

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(H, seed=42)

    nx.draw(
        H,
        pos,
        with_labels=True,
        node_size=500,
        font_size=8
    )

    plt.title("CTI Network Graph")
    plt.tight_layout()
    plt.show()

def community_detection(G):
    communities = nx.community.greedy_modularity_communities(G)

    rows = []

    for idx, community in enumerate(communities):
        for node in community:
            rows.append({
                "community": idx,
                "node": node,
                "type": G.nodes[node].get("type")
            })

    community_df = pd.DataFrame(rows)

    print("="*60)
    print("GRAPH COMMUNITIES")
    print("="*60)
    print(community_df)

    return community_df

def plot_shared_indicators(shared_df, top_n=20):
    if shared_df.empty:
        print("No shared indicators found between actors.")
        return

    data = shared_df.head(top_n).copy()
    data["actor_pair"] = data["actor_1"] + " ↔ " + data["actor_2"]

    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=data,
        y="actor_pair",
        x="shared_indicators"
    )

    plt.title(f"Top {top_n} Actor Pairs by Shared Indicators")
    plt.xlabel("Number of Shared Indicators")
    plt.ylabel("Actor Pair")
    plt.tight_layout()
    plt.show()

def plot_centrality(centrality_df, metric="degree_centrality", top_n=20):
    data = centrality_df.sort_values(
        by=metric,
        ascending=False
    ).head(top_n)

    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=data,
        y="node",
        x=metric,
        hue="type",
        dodge=False
    )

    plt.title(f"Top {top_n} Nodes by {metric}")
    plt.xlabel(metric)
    plt.ylabel("Node")
    plt.legend(title="Node Type")
    plt.tight_layout()
    plt.show()

def plot_community_sizes(community_df):
    sizes = (
        community_df.groupby("community")
        .size()
        .reset_index(name="nodes")
        .sort_values(by="nodes", ascending=False)
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=sizes,
        x="community",
        y="nodes"
    )

    plt.title("Community Size Distribution")
    plt.xlabel("Community ID")
    plt.ylabel("Number of Nodes")
    plt.tight_layout()
    plt.show()

    return sizes

def plot_node_types_per_community(community_df):
    table = pd.crosstab(
        community_df["community"],
        community_df["type"]
    )

    plt.figure(figsize=(12, 7))
    sns.heatmap(
        table,
        annot=True,
        fmt="d",
        cmap="Blues"
    )

    plt.title("Node Types per Community")
    plt.xlabel("Node Type")
    plt.ylabel("Community ID")
    plt.tight_layout()
    plt.show()

    return table

def plot_graph_communities(G, community_df, max_nodes=120):
    community_map = dict(
        zip(community_df["node"], community_df["community"])
    )

    if G.number_of_nodes() > max_nodes:
        selected_nodes = list(G.nodes())[:max_nodes]
        H = G.subgraph(selected_nodes).copy()
    else:
        H = G.copy()

    node_colors = [
        community_map.get(node, -1)
        for node in H.nodes()
    ]

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(H, seed=42)

    nx.draw_networkx_nodes(
        H,
        pos,
        node_color=node_colors,
        cmap=plt.cm.tab20,
        node_size=500
    )

    nx.draw_networkx_edges(
        H,
        pos,
        alpha=0.4
    )

    nx.draw_networkx_labels(
        H,
        pos,
        font_size=7
    )

    plt.title("CTI Graph Colored by Community")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def plot_actor_centrality(centrality_df, metric="degree_centrality", top_n=20):
    data = centrality_df[
        centrality_df["type"] == "actor"
    ].sort_values(
        by=metric,
        ascending=False
    ).head(top_n)

    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=data,
        y="node",
        x=metric
    )

    plt.title(f"Top {top_n} Actors by {metric}")
    plt.xlabel(metric)
    plt.ylabel("Actor")
    plt.tight_layout()
    plt.show()
def plot_actor_indicator_graph(G_ai, max_nodes=100):
    # Limit size for readability
    if G_ai.number_of_nodes() > max_nodes:
        nodes = list(G_ai.nodes())[:max_nodes]
        H = G_ai.subgraph(nodes)
    else:
        H = G_ai

    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(H, seed=42)

    # Color by node type
    colors = []
    for node in H.nodes():
        if H.nodes[node]["type"] == "actor":
            colors.append("red")
        else:
            colors.append("blue")

    nx.draw(
        H,
        pos,
        with_labels=True,
        node_color=colors,
        node_size=500,
        font_size=8
    )

    plt.title("Actor ↔ Indicator Graph")
    plt.tight_layout()
    plt.show()

def plot_bipartite_actor_indicator(G_ai, max_nodes=100):
    # Limit graph size
    if G_ai.number_of_nodes() > max_nodes:
        nodes = list(G_ai.nodes())[:max_nodes]
        H = G_ai.subgraph(nodes)
    else:
        H = G_ai

    # Separate node sets
    actors = [n for n, d in H.nodes(data=True) if d["type"] == "actor"]
    indicators = [n for n, d in H.nodes(data=True) if d["type"] == "indicator"]

    # Create bipartite layout
    pos = {}
    pos.update((node, (0, i)) for i, node in enumerate(actors))
    pos.update((node, (1, i)) for i, node in enumerate(indicators))

    plt.figure(figsize=(14, 10))

    nx.draw_networkx_nodes(H, pos, nodelist=actors, node_color="red", label="Actors")
    nx.draw_networkx_nodes(H, pos, nodelist=indicators, node_color="blue", label="Indicators")

    nx.draw_networkx_edges(H, pos, alpha=0.4)
    nx.draw_networkx_labels(H, pos, font_size=7)

    plt.title("Actor ↔ Indicator Bipartite Graph")
    plt.legend()
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def plot_actor_projection(df, top_n=30):
    import itertools

    # Build mapping
    actor_indicators = df.groupby("actor_name")["indicator_id"].apply(set)

    G = nx.Graph()

    for a1, a2 in itertools.combinations(actor_indicators.index, 2):
        shared = actor_indicators[a1].intersection(actor_indicators[a2])

        if len(shared) > 0:
            G.add_edge(a1, a2, weight=len(shared))

    # Keep strongest relationships
    edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    edges = edges[:top_n]

    H = nx.Graph()
    for u, v, d in edges:
        H.add_edge(u, v, weight=d['weight'])

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(H, seed=42)

    weights = [d['weight'] for _, _, d in H.edges(data=True)]

    nx.draw(
        H,
        pos,
        with_labels=True,
        width=weights,
        node_size=700,
        font_size=8
    )

    plt.title("Actor Relationship Graph (Shared Indicators)")
    plt.tight_layout()
    plt.show()

def build_actor_indicator_bipartite(df):
    B = nx.Graph()

    for _, row in df.iterrows():
        actor = f"A::{row['actor_name']}"
        indicator = f"I::{row['indicator_id']}"

        # Add nodes with bipartite attribute
        B.add_node(actor, bipartite=0, type="actor")
        B.add_node(indicator, bipartite=1, type="indicator")

        # Edge between actor and indicator
        B.add_edge(actor, indicator)

    print(f"Nodes: {B.number_of_nodes()}, Edges: {B.number_of_edges()}")
    return B

def plot_bipartite_graph(B, max_nodes=100):
    # Reduce size for readability
    if B.number_of_nodes() > max_nodes:
        nodes = list(B.nodes())[:max_nodes]
        H = B.subgraph(nodes)
    else:
        H = B

    # Separate node sets
    actors = [n for n, d in H.nodes(data=True) if d["bipartite"] == 0]
    indicators = [n for n, d in H.nodes(data=True) if d["bipartite"] == 1]

    # Position: actors left, indicators right
    pos = {}
    pos.update((node, (0, i)) for i, node in enumerate(actors))
    pos.update((node, (1, i)) for i, node in enumerate(indicators))

    plt.figure(figsize=(14, 10))

    # Draw nodes
    nx.draw_networkx_nodes(H, pos, nodelist=actors, node_color="red", node_size=500, label="Actors")
    nx.draw_networkx_nodes(H, pos, nodelist=indicators, node_color="blue", node_size=500, label="Indicators")

    # Draw edges
    nx.draw_networkx_edges(H, pos, alpha=0.4)

    # Labels
    nx.draw_networkx_labels(H, pos, font_size=7)

    plt.title("Actor ↔ Indicator Bipartite Graph")
    plt.legend()
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def plot_bipartite_spring(B, max_nodes=150):
    if B.number_of_nodes() > max_nodes:
        nodes = list(B.nodes())[:max_nodes]
        H = B.subgraph(nodes)
    else:
        H = B

    pos = nx.spring_layout(H, seed=42)

    colors = [
        "red" if H.nodes[n]["type"] == "actor" else "blue"
        for n in H.nodes()
    ]

    plt.figure(figsize=(14, 10))

    nx.draw(
        H,
        pos,
        node_color=colors,
        with_labels=True,
        node_size=500,
        font_size=7
    )

    plt.title("Actor ↔ Indicator Graph (Spring Layout)")
    plt.tight_layout()
    plt.show()

def network_analysis(df: pd.DataFrame):
    G = build_cti_graph(df)
    centrality_df = graph_centrality_analysis(G)
    G_ai = build_actor_indicator_graph(df)
    shared_df = shared_indicators_between_actors(df)
    community_df = community_detection(G)
    plot_graph(G, max_nodes=80)
    plot_graph(G_ai, max_nodes=80)
    plot_shared_indicators(shared_df, top_n=20)
    plot_centrality(centrality_df, "degree_centrality")
    plot_centrality(centrality_df, "betweenness_centrality")
    plot_centrality(centrality_df, "closeness_centrality")
    community_sizes = plot_community_sizes(community_df)
    community_type_table = plot_node_types_per_community(community_df)
    plot_graph_communities(G, community_df, max_nodes=120)
    plot_actor_centrality(centrality_df, "degree_centrality")
    plot_actor_centrality(centrality_df, "betweenness_centrality")
    plot_actor_indicator_graph(G_ai)
    plot_bipartite_actor_indicator(G_ai)

    # Advanced projection
    plot_actor_projection(df)

    B = build_actor_indicator_bipartite(df)
    plot_bipartite_graph(B, max_nodes=80)
    plot_bipartite_spring(B, max_nodes=150)

def plot_compare_sets(set_ta_dataset,set_cti_pool_dataset) -> None:
    plt.figure(figsize=(6, 6))

    venn2(
        [set_ta_dataset,set_cti_pool_dataset],
        set_labels=("TA dataset", "CTI Pool Dataset")
    )
    plt.show()


def plot_compare_sets_v1(set_ta_dataset, set_cti_pool_dataset) -> None:
    only_ta_dataset = len(set_ta_dataset - set_cti_pool_dataset)
    only_cti_pool_dataset = len(set_cti_pool_dataset - set_ta_dataset)
    both = len(set_ta_dataset & set_cti_pool_dataset)

    total = len(set_ta_dataset | set_cti_pool_dataset)

    print(f"Only TA Dataset: {only_ta_dataset} ({only_ta_dataset / total:.2%})")
    print(f"Only CTI Pool Dataset: {only_cti_pool_dataset} ({only_cti_pool_dataset / total:.2%})")
    print(f"Overlap: {both} ({both / total:.2%})")

    plt.figure(figsize=(6, 6))

    v=venn2(
        [set_ta_dataset,set_cti_pool_dataset],
        set_labels=("TA dataset", "CTI Pool Dataset")
    )
    if v.get_label_by_id('10'):
        v.get_label_by_id('10').set_text(
            f"{only_ta_dataset}\n({only_ta_dataset / total:.1%})"
        )

    if v.get_label_by_id('01'):
        v.get_label_by_id('01').set_text(
            f"{only_cti_pool_dataset}\n({only_cti_pool_dataset / total:.1%})"
        )

    if v.get_label_by_id('11'):
        v.get_label_by_id('11').set_text(
            f"{both}\n({both / total:.1%})"
        )
    plt.show()


