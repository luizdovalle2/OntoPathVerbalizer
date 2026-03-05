import pandas as pd
from graph_reasoning.utils import class_definition
from graph_reasoning.context import extract_context
from graph_reasoning.graph_builder import GraphState

prompt_g_reason = '''
{PATHS}

You are provided with a list of paths between CIDOC-CRM classes. These paths represent a class-level overview of all possible connections between two nodes: {P1} and {P2}. 

Your task is to analyze the graph structure and explain, in clear human-readable English, the possible relationships between these two nodes.

Provide ONLY the human-readable report describing the possible connections.

Definitions of the classes:
{CLASSES}

RDF subgraph containing the relevant individuals:
{RDF}

Ontology dictionary (for internal understanding only):
- Occupational activity: a type of work performed by a person at an institution. The institution is modeled as a group that participates in the event.
- Educational activity: a type of study undertaken by a person at an institution. The institution is modeled as a group that participates in the event.
- Production event: the event during which a physical copy of a book is produced.
- Creation event: the intellectual creation of the idea or content of a book.

IMPORTANT:  
These explanations are provided only for your internal reasoning. Do NOT mention anything about the data structure, RDF, the ontology, or modeling decisions in your response.

Instructions for the report:
- Write only the human-readable explanation.
- Do NOT cite properties, identifiers, or instance labels.
- The reader should not need to know anything about the ontology.
- Do NOT include an introduction.
- Focus on explaining the classes and their roles in the possible connections.
- When referring to a person or a place, provide a concrete example (e.g., a person such as "Jane Austen" or a place such as "Paris").
- Be specific when describing the possible connections.
- Ensure that members of a class are not repeated along the same path.
- Do NOT make assumptions that are not supported by the provided data.

Finally, provide a short summary of the possible relationships. 
'''

def build_prompt(df: pd.DataFrame, state: GraphState, config: dict, source_label: str, target_label: str) -> str:
    """Format full prompt with paths, classes, RDF TTL."""
    path_str = '\n\n'.join(f"path {i+1}\n{txt}" for i, txt in enumerate(df['format_p_cls']))
    classes_list = [class_definition(state.rdf_graph, cls) for cls in df['cls_list'].explode().dropna().unique()]
    ttl = extract_context(state, df['paths_list'].explode().tolist(), config)  # path_nodes from df
    return prompt_g_reason.format(CLASSES=str(classes_list), P1=source_label, P2=target_label, PATHS=path_str, RDF=ttl)
