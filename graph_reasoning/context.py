from typing import List, Set
from rdflib import Graph, URIRef, RDFS, RDF
from graph_reasoning.graph_builder import GraphState

PRODS_PROPS = [
    URIRef("http://www.cidoc-crm.org/cidoc-crm/P108_has_produced"),
    URIRef("http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"),
    URIRef("http://www.cidoc-crm.org/cidoc-crm/P94_has_created"),
    URIRef("http://www.cidoc-crm.org/cidoc-crm/P94i_was_created_by")
]

LABEL_PROP = URIRef("http://www.w3.org/2000/01/rdf-schema#label")
TYPE_PROP = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

def extract_context(state: GraphState, path_nodes: List[str], config: dict) -> str:
    """
    Extract Turtle subgraph: path nodes + production props expansion + extended_prop + labels/types.
    
    Args:
        state: GraphState with G (unused here) and rdf_graph.
        path_nodes: Short names (e.g., ['nd1', 'nd2']) from exploded paths.
        config: Loaded config with 'extended_prop'.
    
    Returns:
        TTL string for LLM prompt.
    """
    g = state.rdf_graph
    extended_prop = config["extended_prop"]
    
    # Extract short names (already done)
    print(f"Path nodes: {path_nodes}")
    
    # Phase 1: Expand via prods_props
    expanded_nodes: Set[str] = set(path_nodes)
    new_neighbors = set()
    for node in list(expanded_nodes):
        uri = URIRef(f"http://onto.uj.edu.pl#{node}")
        # Outgoing
        for p, o in g.predicate_objects(uri):
            if p in PRODS_PROPS:
                new_neighbors.add(str(o).split('#')[-1])
        # Incoming
        for s, p in g.subject_predicates(uri):
            if p in PRODS_PROPS:
                new_neighbors.add(str(s).split('#')[-1])
        expanded_nodes.update(new_neighbors)
    
    # Phase 2: Expand via extended_prop
    new_neighbors = set()
    for node in list(expanded_nodes):
        uri = URIRef(f"http://onto.uj.edu.pl#{node}")
        # Outgoing
        for p, o in g.predicate_objects(uri):
            if p in extended_prop:
                new_neighbors.add(str(o).split('#')[-1])
        # Incoming
        for s, p in g.subject_predicates(uri):
            if p in extended_prop:
                new_neighbors.add(str(s).split('#')[-1])
        expanded_nodes.update(new_neighbors)
    
    # Full URIs
    context_nodes = [f"http://onto.uj.edu.pl#{nd}" for nd in expanded_nodes]
    context_nodes_set = set(context_nodes)
    
    # New subgraph
    context_rdf = Graph()
    
    # 1. Main triples between context nodes
    for s, p, o in g:
        if str(s) in context_nodes_set and str(o) in context_nodes_set:
            context_rdf.add((s, p, o))
    
    # 2. Add rdfs:label (even to literals) and rdf:type triples
    for node_uri in context_nodes:
        uri = URIRef(node_uri)
        # Outgoing labels/types
        for p, o in g.predicate_objects(uri):
            if p == LABEL_PROP:
                context_rdf.add((uri, p, o))
            if p == TYPE_PROP:
                context_rdf.add((uri, p, URIRef(o)))
    
    print(f"Total triples: {len(context_rdf)} (incl. {sum(1 for s,p,o in context_rdf if p == LABEL_PROP)} labels)")
    
    # Prefixes for clean TTL
    context_rdf.bind("onto", "http://onto.uj.edu.pl")
    context_rdf.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    context_rdf.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    context_rdf.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    
    ttl = context_rdf.serialize(format="turtle")
    return ttl
