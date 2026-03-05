from typing import Optional
from rdflib import Graph, URIRef, RDF, RDFS, OWL
import networkx as nx
from graph_reasoning.config import load_config

CLS_KEY = 'cls'

class GraphState:
    """Holds RDF Graph and NetworkX DiGraph."""
    def __init__(self, G: nx.DiGraph, rdf_graph: Graph):
        self.G = G
        self.rdf_graph = rdf_graph

def ensure_node_with_cls(u: URIRef, G: nx.DiGraph, rdf_graph: Graph) -> str:
    """Add node with RDF types if missing."""
    u_str = str(u)
    if u_str in G:
        return u_str
    types = {str(t) for t in rdf_graph.objects(u, RDF.type)}
    G.add_node(u_str, **{CLS_KEY: types})
    return u_str

def initialize_graph(rdf_path: str, config: dict, format: str = "xml") -> GraphState:
    """Build NetworkX DiGraph from RDF, respecting config removes."""
    g = Graph()
    g.parse(rdf_path, format=format)
    G = nx.DiGraph()
    
    # Inverse map
    inv_map = {}
    for p, inv in g.subject_objects(OWL.inverseOf):
        inv_map[p] = inv
        inv_map[inv] = p
    
    # Add edges
    nodes_remove = config["nodes_remove"]
    props_remove = config["props_remove"]
    for s, p, o in g:
        if str(p).startswith(str(RDF)): continue
        if p in props_remove: continue
        if s in nodes_remove or o in nodes_remove: continue
        if not (isinstance(s, URIRef) and isinstance(o, URIRef)): continue
        
        s_id = ensure_node_with_cls(s, G, g)
        o_id = ensure_node_with_cls(o, G, g)
        G.add_edge(s_id, o_id, predicate=str(p))
        inv_p = inv_map.get(p)
        if inv_p:
            G.add_edge(o_id, s_id, predicate=str(inv_p))
    
    print(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges")  # [file:1]
    return GraphState(G, g)
