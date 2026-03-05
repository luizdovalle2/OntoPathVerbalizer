from typing import List
from networkx import DiGraph
from rdflib import Graph, URIRef, RDFS

def format_path(G: DiGraph, path: List[str]) -> str:
    """Format path as 'node1 [pred] -> node2 [pred] -> ...'."""
    if len(path) < 2: return str(path)
    formatted = [(path[i], G[path[i]][path[i+1]]['predicate'], path[i+1]) for i in range(len(path)-1)]
    ret = ' -> '.join(f'{u} [{p}]' for u, p, v in formatted)
    return f'{ret} -> {path[-1]}'

def format_path_cls(G: DiGraph, path: List[str], d: dict) -> str:
    """Formatted with labels."""
    if len(path) < 2: return str(path)
    formatted = [(d[path[i]], G[path[i]][path[i+1]]['predicate'], d[path[i+1]]) for i in range(len(path)-1)]
    ret = ' -> '.join(f'{u} [{p}]' for u, p, v in formatted)
    return f'{ret} -> {d[path[-1]]}'

def contains_subpath(longer: str, shorter: str) -> bool:
    shorter, longer = shorter[1:-2], longer[1:-2]
    m, n = len(longer), len(shorter)
    return any(longer[i:i+n] == shorter for i in range(m - n + 1))

def class_definition(g: Graph, class_iri: str, lang: str = "en") -> dict:
    """Extract class metadata."""
    c = URIRef(class_iri)
    def pick_lang(lits):
        lits = list(lits)
        if lang is None: return [str(x) for x in lits]
        preferred = [x for x in lits if getattr(x, 'language', None) == lang]
        return [str(x) for x in preferred or lits]
    return {
        "iri": str(c),
        "comments": pick_lang(g.objects(c, RDFS.comment)),
        "subClassOf": [str(o) for o in g.objects(c, RDFS.subClassOf)],
    }
