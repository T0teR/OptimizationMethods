"""
Генерация данных для ЛР2 — транзитная транспортная задача.
Вариант 2: 3 источника, 2 хаба, 5 потребителей.
Seed = 10213 (как в ЛР1).
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 10213
rng = np.random.default_rng(SEED)

sources = ["S1", "S2", "S3"]
hubs = ["H1", "H2"]
consumers = ["C1", "C2", "C3", "C4", "C5"]

base_supply = np.array([42.0, 35.0, 28.0])
base_demand = np.array([18.0, 22.0, 20.0, 25.0, 20.0])  # сумма = 105 = sum supply

supply = base_supply * rng.uniform(0.97, 1.03, size=3)
demand = base_demand * rng.uniform(0.97, 1.03, size=5)
diff = supply.sum() - demand.sum()
demand[-1] += diff

arcs = []
for s in sources:
    for h in hubs:
        arcs.append((s, h))

for h in hubs:
    for c in consumers:
        arcs.append((h, c))

direct = [("S1", "C1"), ("S1", "C3"), ("S2", "C2"), ("S2", "C5"), ("S3", "C4"), ("S3", "C1")]
arcs.extend(direct)

base_cost = {
    ("S1", "H1"): 4.0, ("S1", "H2"): 6.5,
    ("S2", "H1"): 5.5, ("S2", "H2"): 3.5,
    ("S3", "H1"): 7.0, ("S3", "H2"): 4.5,

    ("H1", "C1"): 3.0, ("H1", "C2"): 4.5, ("H1", "C3"): 2.5,
    ("H1", "C4"): 5.0, ("H1", "C5"): 6.0,
    ("H2", "C1"): 5.5, ("H2", "C2"): 2.0, ("H2", "C3"): 4.0,
    ("H2", "C4"): 3.5, ("H2", "C5"): 3.0,

    ("S1", "C1"): 9.0, ("S1", "C3"): 10.5,
    ("S2", "C2"): 8.5, ("S2", "C5"): 11.0,
    ("S3", "C4"): 9.5, ("S3", "C1"): 12.0,
}

costs = {}
caps = {}
for a in arcs:
    noise = rng.uniform(0.92, 1.08)
    costs[a] = round(base_cost[a] * noise, 4)
    if a[0] in sources and a[1] in hubs:
        caps[a] = round(rng.uniform(28, 45), 2)
    elif a[0] in hubs:
        caps[a] = round(rng.uniform(22, 38), 2)
    else:
        caps[a] = round(rng.uniform(8, 16), 2)


nodes_supply = pd.DataFrame({
    "node": sources,
    "type": "source",
    "supply": supply,
    "demand": 0.0,
})
nodes_hub = pd.DataFrame({
    "node": hubs,
    "type": "hub",
    "supply": 0.0,
    "demand": 0.0,
})
nodes_cons = pd.DataFrame({
    "node": consumers,
    "type": "consumer",
    "supply": 0.0,
    "demand": demand,
})
nodes = pd.concat([nodes_supply, nodes_hub, nodes_cons], ignore_index=True)

arcs_df = pd.DataFrame({
    "from": [a[0] for a in arcs],
    "to": [a[1] for a in arcs],
    "cost": [costs[a] for a in arcs],
    "capacity": [caps[a] for a in arcs],
})

out = Path("data")
out.mkdir(exist_ok=True)
nodes.to_csv(out / "nodes.csv", index=False, encoding="utf-8-sig")
arcs_df.to_csv(out / "arcs.csv", index=False, encoding="utf-8-sig")

print("=== УЗЛЫ ===")
print(nodes.round(4).to_string(index=False))
print("\nСумма supply:", round(supply.sum(), 4), "  Сумма demand:", round(demand.sum(), 4))
print("\n=== ДУГИ (фрагмент) ===")
print(arcs_df.head(15).round(4).to_string(index=False))
print(f"\nВсего дуг: {len(arcs_df)}")
print("Seed:", SEED)
print("Данные сохранены в data/")
