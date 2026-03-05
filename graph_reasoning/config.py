import yaml
from pathlib import Path
from typing import Any
from rdflib import URIRef

def load_config(config_path: str | Path = "config.yml") -> dict[str, Any]:
    """Load YAML config with URIRef conversion for lists."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    config["nodes_remove"] = [URIRef(x) for x in config.get("nodes_remove", [])]
    config["props_remove"] = [URIRef(x) for x in config.get("props_remove", [])]
    config["extended_prop"] = [URIRef(x) for x in config.get("extended_prop", [])]
    config["target_classes"] = [URIRef(x) for x in config["target_classes"]]
    return config
