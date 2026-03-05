#!/usr/bin/env python
from openai import OpenAI
from rdflib import  RDF, RDFS, URIRef

from graph_reasoning.config import load_config
from graph_reasoning.graph_builder import initialize_graph, GraphState
from graph_reasoning.pathfinder import get_paths
from graph_reasoning.prompt import build_prompt

config = load_config()
state = initialize_graph(config["graph_path"], config)


def get_labels_dict():

    TARGET_CLASSES = list(map(lambda x: URIRef(x), config["target_classes"]))

    first_label = {}
    for s in state.rdf_graph.subjects(RDFS.label, None):
        if not any((s, RDF.type, cls) in state.rdf_graph for cls in TARGET_CLASSES):
            continue
        lbl = state.rdf_graph.value(s, RDFS.label, any=True)
        if lbl is not None:
            first_label[str(lbl)] = s
    return first_label

def get_results(source, target):    
    df = get_paths(source, target, state)
    prompt = build_prompt(df, state, config, source, target)
    
    client = OpenAI(api_key=config["api_key"], base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    completion = client.chat.completions.create(model="qwen3-max", messages=[{"role": "user", "content": prompt}])
    return completion.choices[0].message.content
