import graphviz
import os

GRAPH_OUTPUT_DIR = "app/static/graphs"

def render_graph(dot_source: str, subdir: str, name_prefix: str):
    """
    Render a Graphviz DOT source into a PNG file and return its file path.
    """
    os.makedirs(os.path.join(GRAPH_OUTPUT_DIR, subdir), exist_ok=True)


    graph_path = os.path.join(GRAPH_OUTPUT_DIR, subdir, name_prefix)

    try:
        graphviz.Source(dot_source).render(graph_path, format='png', cleanup=True)
        return f"/graphs/{subdir}/{name_prefix}.png"
    except Exception as e:
        return f"Failed to render graph: {e}"