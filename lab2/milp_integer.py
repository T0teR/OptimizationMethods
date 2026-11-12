"""
Задание со звёздочкой №1:
Целочисленные (неделимые) перевозки — сравнение LP-релаксации и MILP.
Потоки округляются до целых единиц груза.
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog, milp, LinearConstraint, Bounds

nodes = pd.read_csv("data/nodes.csv")
arcs = pd.read_csv("data/arcs.csv")

sources = nodes[nodes["type"] == "source"]["node"].tolist()
hubs = nodes[nodes["type"] == "hub"]["node"].tolist()
consumers = nodes[nodes["type"] == "consumer"]["node"].tolist()
supply = {r["node"]: int(round(r["supply"])) for _, r in nodes[nodes["type"] == "source"].iterrows()}
demand = {r["node"]: int(round(r["demand"])) for _, r in nodes[nodes["type"] == "consumer"].iterrows()}

diff = sum(supply.values()) - sum(demand.values())
if diff != 0:
    last = consumers[-1]
    demand[last] += diff

arc_list = list(zip(arcs["from"], arcs["to"]))
n_arcs = len(arc_list)
cost = arcs["cost"].to_numpy()
cap = np.array([int(np.floor(c)) for c in arcs["capacity"]])  # целые ёмкости

def build_eq():
    rows = []
    rhs = []
    for s in sources:
        row = np.zeros(n_arcs)
        for j, (fr, to) in enumerate(arc_list):
            if fr == s:
                row[j] = 1.0
        rows.append(row)
        rhs.append(supply[s])
    for c in consumers:
        row = np.zeros(n_arcs)
        for j, (fr, to) in enumerate(arc_list):
            if to == c:
                row[j] = 1.0
        rows.append(row)
        rhs.append(demand[c])
    for h in hubs:
        row = np.zeros(n_arcs)
        for j, (fr, to) in enumerate(arc_list):
            if to == h:
                row[j] = 1.0
            if fr == h:
                row[j] = -1.0
        rows.append(row)
        rhs.append(0.0)
    return np.vstack(rows), np.array(rhs)

A_eq, b_eq = build_eq()
bounds_lp = [(0, float(cap[i])) for i in range(n_arcs)]

lp = linprog(cost, A_eq=A_eq, b_eq=b_eq, bounds=bounds_lp, method="highs")
print("LP-релаксация: success =", lp.success, "  cost =", round(lp.fun, 6) if lp.success else None)

constraints = LinearConstraint(A_eq, b_eq, b_eq)
bounds_m = Bounds(0, cap.astype(float))
integrality = np.ones(n_arcs)

milp_res = milp(
    c=cost,
    constraints=constraints,
    bounds=bounds_m,
    integrality=integrality,
    options={"disp": False},
)

print("MILP (integer flows): success =", milp_res.success,
      "  cost =", round(milp_res.fun, 6) if milp_res.success else None)

if lp.success and milp_res.success:
    gap = milp_res.fun - lp.fun
    print(f"Интегральный зазор: {gap:.6f} ({100 * gap / lp.fun:.3f}%)")
    print("\nСравнение потоков (ненулевые):")
    cmp = pd.DataFrame({
        "from": [a[0] for a in arc_list],
        "to": [a[1] for a in arc_list],
        "lp_flow": lp.x,
        "milp_flow": milp_res.x,
    })
    cmp = cmp[(cmp["lp_flow"] > 1e-6) | (cmp["milp_flow"] > 1e-6)]
    print(cmp.round(4).to_string(index=False))
    cmp.to_csv("lp_vs_milp.csv", index=False, encoding="utf-8-sig")
    print("\nСохранено: lp_vs_milp.csv")
else:
    print("Одно из решений не найдено")
    if not milp_res.success:
        print("MILP message:", milp_res.message)
