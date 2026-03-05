# OntoPathVerbalizer

**Code used for paper *OntoPathVerbalizer: a Tool for Classifying and Verbalizing Connections in Knowledge Graphs*.**

Interactive Streamlit app for **pathfinding between entities** (people, places, institutions, books) in RDF knowledge graphs.

## 🚀 Step-by-Step Setup

1. **Clone & Navigate**
   ```bash
   git clone <repo-url>
   cd OntoPathVerbalizer
   ```

2. **Configure**
   ```bash
   cp config.yml.dist config.yml
   ```
   Edit `config.yml`:
   ```yaml
   grath_path: "your_graph.rdf"     # Place RDF here ↓
   name_space: "http://onto.uj.edu.pl#"
   target_classes:
     - "http://example.org/Person"
     - "http://example.org/Place"
   nodes_remove: 
        - ...
        - ...
   props_remove: 
        -  "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        -   ...
   extended_prop: 
        - ...
        - ...
   ```

3. **Place RDF Graph**
   ```
   your_project/
   ├── your_graph.rdf     # ← Put RDF file here
   ├── config.yml         # ← Edited config
   └── app.py
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run App**
   ```bash
   streamlit run app.py
   ```
   **By default opens**: `http://localhost:8501`

---

## 📁 Repository Structure

```
.
├── app.py                      # Streamlit entrypoint
├── config.yml                  # ← Copy + edit from config.yml.dist
├── config.yml.dist             # Template
├── requirements.txt
└── graph_reasoning/
    ├── __init__.py             # Package init
    ├── config.py               # load_config()
    ├── context.py              # Extract RDF subgraph context
    ├── prompt.py               # Build LLM prompts
    ├── graph_builder.py        # GraphState, initialize_graph()
    ├── pathfinder.py           # get_paths()
    ├── utils.py                # format_path(), class_definition()
    └── reas.py                 # get_labels_dict(), get_results()
```

## 🎯 Usage

1. Select **Entity 1** and **Entity 2** from dropdowns (RDF labels)
2. Click **Run**
3. View **Report with verbalized connecting paths**

