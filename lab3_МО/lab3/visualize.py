"""Визуализация: районы, кандидаты, открытые вышки и покрытие."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

Path("figures").mkdir(exist_ok=True)

sites = pd.read_csv("data/sites.csv")
districts = pd.read_csv("data/districts.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)
sol = pd.read_csv("solution.csv")

opened = set(sol.loc[sol["open"] == 1, "site"])

fig, ax = plt.subplots(figsize=(9, 7))


ax.scatter(districts["x"], districts["y"], c="#2196F3", s=80, label="Район", zorder=3)
for _, r in districts.iterrows():
    ax.annotate(r["district"], (r["x"], r["y"]), textcoords="offset points",
                xytext=(4, 4), fontsize=7)


for _, r in sites.iterrows():
    if r["site"] in opened:
        ax.scatter(r["x"], r["y"], c="#4CAF50", s=160, marker="^", zorder=4)
        ax.annotate(r["site"], (r["x"], r["y"]), textcoords="offset points",
                    xytext=(5, 5), fontsize=8, fontweight="bold", color="#2E7D32")
    else:
        ax.scatter(r["x"], r["y"], c="#BDBDBD", s=100, marker="^", zorder=2)
        ax.annotate(r["site"], (r["x"], r["y"]), textcoords="offset points",
                    xytext=(4, 4), fontsize=7, color="#757575")


for sname in opened:
    j = list(sites["site"]).index(sname)
    sx, sy = sites.loc[j, ["x", "y"]]
    for i, dname in enumerate(coverage.index):
        if coverage.loc[dname, sname] == 1:
            dx, dy = districts.loc[i, ["x", "y"]]
            ax.plot([sx, dx], [sy, dy], color="#81C784", alpha=0.35, lw=0.9, zorder=1)

from matplotlib.lines import Line2D
legend = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#2196F3", markersize=8, label="Район"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="#4CAF50", markersize=10, label="Открытая вышка"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="#BDBDBD", markersize=10, label="Кандидат (закрыт)"),
]
ax.legend(handles=legend, loc="best")
ax.set_title("Оптимальное размещение вышек (set covering)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_aspect("equal")
plt.tight_layout()
plt.savefig("figures/coverage_map.png", dpi=150, bbox_inches="tight")
print("Сохранено: figures/coverage_map.png")
plt.close()
