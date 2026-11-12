"""
Задание со звёздочкой №2:
Двойственная интерпретация — потенциалы узлов, условие оптимальности дуг,
проверка равенства целей прямой и двойственной задач.
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog

nodes = pd.read_csv("data/nodes.csv")
arcs = pd.read_csv("data/arcs.csv")
flows = pd.read_csv("solution_flows.csv")

sources = nodes[nodes["type"] == "source"]["node"].tolist()
hubs = nodes[nodes["type"] == "hub"]["node"].tolist()
consumers = nodes[nodes["type"] == "consumer"]["node"].tolist()
supply = nodes.set_index("node")["supply"].to_dict()
demand = nodes.set_index("node")["demand"].to_dict()

arc_list = list(zip(arcs["from"], arcs["to"]))
n_arcs = len(arc_list)
cost = arcs["cost"].to_numpy()
cap = arcs["capacity"].to_numpy()

A_eq_rows = []
b_eq = []
for s in sources:
    row = np.zeros(n_arcs)
    for j, (fr, to) in enumerate(arc_list):
        if fr == s:
            row[j] = 1.0
    A_eq_rows.append(row)
    b_eq.append(supply[s])
for c in consumers:
    row = np.zeros(n_arcs)
    for j, (fr, to) in enumerate(arc_list):
        if to == c:
            row[j] = 1.0
    A_eq_rows.append(row)
    b_eq.append(demand[c])
for h in hubs:
    row = np.zeros(n_arcs)
    for j, (fr, to) in enumerate(arc_list):
        if to == h:
            row[j] = 1.0
        if fr == h:
            row[j] = -1.0
    A_eq_rows.append(row)
    b_eq.append(0.0)

A_eq = np.vstack(A_eq_rows)
b_eq = np.array(b_eq)
bounds = [(0, float(cap[i])) for i in range(n_arcs)]

res = linprog(cost, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
assert res.success

labels = sources + consumers + hubs
potentials = dict(zip(labels, res.eqlin.marginals))

print("Потенциалы узлов (двойственные переменные балансов):")
for n, p in potentials.items():
    print(f"  {n}: {p:.6f}")


print("\nПроверка приведённых стоимостей на используемых дугах:")
flow_map = {(r["from"], r["to"]): r["flow"] for _, r in flows.iterrows()}

rows = []
for j, (fr, to) in enumerate(arc_list):
    f = flow_map.get((fr, to), 0.0)
    pi_fr = potentials.get(fr, 0.0)
    pi_to = potentials.get(to, 0.0)
    reduced = cost[j] + pi_fr - pi_to
    rows.append({
        "from": fr,
        "to": to,
        "cost": cost[j],
        "flow": f,
        "potential_from": pi_fr,
        "potential_to": pi_to,
        "reduced_cost": reduced,
        "active": f > 1e-6,
    })

rc = pd.DataFrame(rows)
print(rc[rc["active"]].round(5).to_string(index=False))

primal = res.fun
dual = float(np.dot(b_eq, res.eqlin.marginals))
print(f"\nПрямая цель: {primal:.6f}")
print(f"Двойственная цель (bᵀπ): {dual:.6f}")
print(f"Разность: {abs(primal - dual):.2e}")

rc.to_csv("reduced_costs.csv", index=False, encoding="utf-8-sig")
print("Сохранено: reduced_costs.csv")