import pandas as pd
import re
import numpy as np
from typing import List, Optional
from networkx import DiGraph
from rdflib import Graph, RDFS
import re
from graph_reasoning.utils import format_path, format_path_cls, contains_subpath
import swifter

def node_types(n: str, G: DiGraph, cls_key: str = 'cls') -> str:
    """Get primary RDF type for node."""
    t = G.nodes[n].get(cls_key, set())
    ret = t if isinstance(t, set) else set(t)
    return list(ret)[0] if ret else ""

def get_paths(source_label: str, target_label: str, state: 'GraphState') -> pd.DataFrame:
    """BFS pathfinding to target, with minimal non-subpath selection."""
    G, g = state.G, state.rdf_graph
    source = sorted(s for s, lbl in g.subject_objects(RDFS.label) if str(lbl) == source_label)[0]
    target = str(sorted(s for s, lbl in g.subject_objects(RDFS.label) if str(lbl) == target_label)[0])
    source_str = str(source)
    
    # Init BFS DF
    i = 0
    df = pd.DataFrame({f"path_{i}": list(G.successors(source_str))})
    df[f"cls_{i}"] = df[f"path_{i}"].map(lambda n: node_types(n, G))
    path_cols = []
    complete_df_list, stopped_df_list = [], []
    
    visited_paths = {source_str}
    df["visited"] = df[f"path_{i}"].apply(lambda x: (source_str, str(x)))
    
    while not df.empty:
        i += 1
        prev_col, cur_col = f"path_{i-1}", f"path_{i}"
        df[cur_col] = df[prev_col].map(lambda x: list(G.successors(str(x))))
        df = df.explode(cur_col, ignore_index=True).dropna(subset=[cur_col])
        
        # Visited check
        tmp = df.swifter.apply(
            lambda r: (r[cur_col] not in r["visited"], r["visited"] + (r[cur_col],)),
            axis=1
        )
        keep = tmp.str[0]
        df = df.loc[keep].copy()
        df["visited"] = tmp.loc[keep].str[1].to_numpy()
        
        path_cols.append(f"path_{i-1}")
        visited_paths |= set(df[path_cols].to_numpy().ravel())
        df.loc[:, "stopped"] = df[cur_col].isin(visited_paths)
        
        df = df.drop_duplicates(subset=[f"cls_{i-1}", cur_col])
        df.loc[:, f"cls_{i}"] = df[cur_col].map(lambda n: node_types(n, G))
        
        # Stopped paths
        cur_stop_df = df[df['stopped']].copy()
        cur_stop_df["stopped_path"] = cur_stop_df[cur_col]
        cur_stop_df["stopped_path_number"] = i
        stopped_df_list.append(cur_stop_df)
        df = df[~df['stopped']]
        
        # Complete to target
        done = df[cur_col].eq(target)
        if done.any():
            complete_df_list.append(df.loc[done].copy())
        df = df.loc[~done].copy()
    
    if not complete_df_list:
        raise ValueError("No path found between entities")
    
    # Merge stopped into completes (your complex logic preserved, cleaned)
    complete_df = pd.concat(complete_df_list, ignore_index=True)
    stopped_df = pd.concat(stopped_df_list, ignore_index=True)
    path_cols = [k for k in complete_df if k.startswith("path")]
    complete_nodes = complete_df[path_cols].dropna().values.ravel().tolist()
    stopped_df = stopped_df[stopped_df.stopped_path.isin(complete_nodes)].reset_index(drop=True)
    

    stopped_df = stopped_df.reset_index(drop=True).reset_index()
    merged_dfs_list = []
    for ind_col, col in enumerate(path_cols):   
        merged_df = stopped_df.merge(complete_df, left_on='stopped_path', right_on=col, how='inner')
        if len(merged_df):
            merged_df = merged_df.replace("", np.nan).dropna(axis=1, how="all")
            rep_dict = {}
            for idx, row in merged_df.iterrows():

                for el in merged_df.columns:
            
                    if el.endswith("_x"):
                        rep_dict[el] = el.replace("_x","")
                    if el.endswith("_y") and  el.startswith("path_"):
                        cur_i = int(el.replace("_y","").replace("path_","")) 
                        if cur_i <= ind_col:
                            continue
                        v =  cur_i + row["stopped_path_number"] - ind_col
                        rep_dict[el] = f"path_{v}"
                    if el.endswith("_y") and  el.startswith("cls_"):
                        cur_i = int(el.replace("_y","").replace("cls_","")) 
                        if cur_i <= ind_col:
                            continue
                        v =  cur_i + row["stopped_path_number"] - ind_col
                        rep_dict[el] = f"cls_{v}"
                row = row.rename(rep_dict)
                merged_dfs_list.append(row.to_frame().T)

            stopped_df = stopped_df[~stopped_df["index"].isin(merged_df.index)]
            # merged_dfs_list.append(merged_df)
    df_complete_new = pd.concat(merged_dfs_list)

    path_cols = [k for k in df_complete_new.columns if k.startswith("path") and not k.endswith("_y")]
    cls_cols = [k for k in df_complete_new.columns if k.startswith("cls" ) and not k.endswith("_y")]
    df_complete_new = df_complete_new[path_cols+cls_cols].reset_index(drop=True)
    df_complete_final = pd.concat([complete_df, df_complete_new])

    path_cols = [c for c in df_complete_final.columns if str(c).startswith("path_")]

    path_cols = sorted(
        path_cols,
        key=lambda c: int(re.search(r"^path_(\d+)$", str(c)).group(1))
    )


    df_complete_final = pd.concat([complete_df, df_complete_new], ignore_index=True)

    path_cols = [c for c in df_complete_final.columns if str(c).startswith("path")]

    df_complete_final["paths_list"] = df_complete_final.apply(
        lambda row: row[path_cols].dropna().tolist(),
        axis=1
    )


    class_cols = [c for c in df_complete_final.columns if str(c).startswith("cls")]


    class_cols = sorted(
        class_cols,
        key=lambda c: int(re.search(r"cls_(\d+)$", str(c)).group(1))
    )

    df_complete_final["cls_list"] = df_complete_final.apply(
        lambda row: row[class_cols].dropna().tolist(),
        axis=1
    )
    p_list_unique = df_complete_final["paths_list"]


    # p_list_unique: pandas Series, index = the ids you want to keep
    p_list_unique = p_list_unique.dropna()

    # Sort shortest first, but keep original index on each element
    order = p_list_unique.map(len).sort_values().index  # sort_values sorts by computed lengths [web:72]
    paths_sorted = p_list_unique.loc[order]

    # Keep minimal paths, preserving the original index of each kept path
    kept = []          # values (paths)
    kept_idx = []      # their original indices

    for idx, cand in paths_sorted.items():  # items() yields (index, value) pairs [web:100]
        if any(contains_subpath(cand, small) for small in kept):
            continue
        kept.append(cand)
        kept_idx.append(idx)

    # Result Series: values are paths, index are original indices from p_list_unique
    p_list_minimal = pd.Series(kept, index=kept_idx, name=p_list_unique.name)
    df_complete_final = df_complete_final.loc[p_list_minimal.index]

    df_complete_final["paths_list"] = df_complete_final["paths_list"].apply(lambda x: [str(source)] + x)
    df_complete_final["cls_list"] = df_complete_final["cls_list"].apply(lambda x: [node_types(str(source), G)] + x)
    df_complete_final["conv"] = df_complete_final.apply(lambda row: dict(zip(row.paths_list,row.cls_list )), axis=1)
    df_complete_final["format_p_cls"] = df_complete_final.apply(lambda row: format_path_cls(G, row.paths_list, row.conv ), axis=1)
    df_complete_final["format_path"] = df_complete_final.apply(lambda row: format_path(G, row.paths_list), axis=1)
    
    return df_complete_final
