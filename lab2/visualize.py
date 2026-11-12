"""
Визуализация сети с потоками (NetworkX + matplotlib).
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

Path("figures").mkdir(exist_ok=True)

nodes = pd.read_csv("data/nodes.csv")
arcs = pd.read_csv("data/arcs.csv")
flows = pd.read_csv("solution_flows.csv")

G = nx.DiGraph()

pos = {
    "S1": (0, 2), "S2": (0, 1), "S3": (0, 0),
    "H1": (1.5, 1.7), "H2": (1.5, 0.3),
    "C1": (3, 2.2), "C2": (3, 1.5), "C3": (3, 0.9),
    "C4": (3, 0.4), "C5": (3, -0.2),
}

for _, r in nodes.iterrows():
    G.add_node(r["node"], ntype=r["type"], supply=r["supply"], demand=r["demand"])

flow_map = {(r["from"], r["to"]): r["flow"] for _, r in flows.iterrows()}
cap_map = {(r["from"], r["to"]): r["capacity"] for _, r in arcs.iterrows()}
cost_map = {(r["from"], r["to"]): r["cost"] for _, r in arcs.iterrows()}

for _, r in arcs.iterrows():
    fr, to = r["from"], r["to"]
    f = flow_map.get((fr, to), 0.0)
    G.add_edge(fr, to, flow=f, capacity=r["capacity"], cost=r["cost"])

fig, ax = plt.subplots(figsize=(11, 7))
node_colors = []
for n in G.nodes():
    t = G.nodes[n]["ntype"]
    if t == "source":
        node_colors.append("#4CAF50")
    elif t == "hub":
        node_colors.append("#FF9800")
    else:
        node_colors.append("#2196F3")

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)

edges_with_flow = [(u, v) for u, v, d in G.edges(data=True) if d["flow"] > 1e-6]
edges_zero = [(u, v) for u, v, d in G.edges(data=True) if d["flow"] <= 1e-6]

widths = [1.5 + 4.0 * G[u][v]["flow"] / 30 for u, v in edges_with_flow]
nx.draw_networkx_edges(G, pos, edgelist=edges_with_flow, width=widths,
                       edge_color="#333333", arrows=True, arrowsize=15,
                       connectionstyle="arc3,rad=0.05", ax=ax)
nx.draw_networkx_edges(G, pos, edgelist=edges_zero, width=0.6,
                       edge_color="#cccccc", style="dashed", arrows=True,
                       arrowsize=10, connectionstyle="arc3,rad=0.05", ax=ax,
                       alpha=0.5)

edge_labels = {(u, v): f"{G[u][v]['flow']:.1f}" for u, v in edges_with_flow}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

from matplotlib.patches import Patch
legend = [
    Patch(facecolor="#4CAF50", label="Источник"),
    Patch(facecolor="#FF9800", label="Хаб"),
    Patch(facecolor="#2196F3", label="Потребитель"),
]
ax.legend(handles=legend, loc="upper left")
ax.set_title("Оптимальные потоки (базовый сценарий)")
ax.axis("off")
plt.tight_layout()
plt.savefig("figures/network_flows.png", dpi=150, bbox_inches="tight")
print("Сохранено: figures/network_flows.png")
plt.close()
