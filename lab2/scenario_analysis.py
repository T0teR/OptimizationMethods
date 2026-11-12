"""
Сценарный анализ:
1) Базовый
2) Отказ самой загруженной дуги
3) Рост спроса +20%
+ жадная эвристика
+ теневые цены
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog

nodes = pd.read_csv("data/nodes.csv")
arcs = pd.read_csv("data/arcs.csv")

sources = nodes[nodes["type"] == "source"]["node"].tolist()
hubs = nodes[nodes["type"] == "hub"]["node"].tolist()
consumers = nodes[nodes["type"] == "consumer"]["node"].tolist()

supply = nodes.set_index("node")["supply"].to_dict()
demand = nodes.set_index("node")["demand"].to_dict()

arc_list = list(zip(arcs["from"], arcs["to"]))
n_arcs = len(arc_list)
cost = arcs["cost"].to_numpy().copy()
cap = arcs["capacity"].to_numpy().copy()


def build_and_solve(cap_vec, demand_dict, supply_dict):
    A_eq_rows = []
    b_eq = []
    for s in sources:
        row = np.zeros(n_arcs)
        for j, (fr, to) in enumerate(arc_list):
            if fr == s:
                row[j] = 1.0
        A_eq_rows.append(row)
        b_eq.append(supply_dict[s])
    for c in consumers:
        row = np.zeros(n_arcs)
        for j, (fr, to) in enumerate(arc_list):
            if to == c:
                row[j] = 1.0
        A_eq_rows.append(row)
        b_eq.append(demand_dict[c])
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
    bounds = [(0, float(cap_vec[i])) for i in range(n_arcs)]
    return linprog(cost, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")


base = build_and_solve(cap, demand, supply)
print("Базовый: success =", base.success, "  cost =", round(base.fun, 4) if base.success else None)

flows = base.x
busy_idx = int(np.argmax(flows))
busy_arc = arc_list[busy_idx]
print(f"Самая загруженная дуга: {busy_arc[0]}->{busy_arc[1]}, flow={flows[busy_idx]:.3f}")

cap_fail = cap.copy()
cap_fail[busy_idx] = 0.0
fail = build_and_solve(cap_fail, demand, supply)
print("Отказ дуги: success =", fail.success, "  cost =", round(fail.fun, 4) if fail.success else "Infeasible")

demand_up = {c: demand[c] * 1.2 for c in consumers}
grow = build_and_solve(cap, demand_up, supply)
print("Спрос +20% (жёстко): success =", grow.success,
      "  cost =", round(grow.fun, 4) if grow.success else "Infeasible")

rows = []
for name, res in [
    ("Базовый", base),
    (f"Отказ {busy_arc[0]}->{busy_arc[1]}", fail),
    ("Спрос +20%", grow),
]:
    rows.append({
        "scenario": name,
        "status": "Optimal" if res.success else "Infeasible",
        "cost": res.fun if res.success else np.nan,
        "total_flow": float(np.sum(res.x)) if res.success else np.nan,
    })
scenario_df = pd.DataFrame(rows)
print("\n", scenario_df.to_string(index=False))
scenario_df.to_csv("scenario_results.csv", index=False, encoding="utf-8-sig")

if base.success and base.eqlin is not None:
    labels = sources + consumers + hubs
    shadow = pd.DataFrame({"node": labels, "shadow_price": base.eqlin.marginals})
    print("\nТеневые цены (потенциалы узлов):")
    print(shadow.round(6).to_string(index=False))
    shadow.to_csv("shadow_prices.csv", index=False, encoding="utf-8-sig")

print("\n=== ЖАДНАЯ ЭВРИСТИКА ===")
paths = []

for j, (fr, to) in enumerate(arc_list):
    if fr in sources and to in consumers:
        paths.append((cost[j], [j], fr, to))

for j1, (fr1, to1) in enumerate(arc_list):
    if fr1 in sources and to1 in hubs:
        for j2, (fr2, to2) in enumerate(arc_list):
            if fr2 == to1 and to2 in consumers:
                paths.append((cost[j1] + cost[j2], [j1, j2], fr1, to2))

paths.sort(key=lambda p: p[0])

rem_s = supply.copy()
rem_d = demand.copy()
rem_cap = cap.copy()
greedy_flow = np.zeros(n_arcs)

for pcost, idxs, s, c in paths:
    if rem_s[s] <= 1e-12 or rem_d[c] <= 1e-12:
        continue
    can = min(rem_s[s], rem_d[c])
    for j in idxs:
        can = min(can, rem_cap[j])
    if can <= 1e-12:
        continue
    for j in idxs:
        greedy_flow[j] += can
        rem_cap[j] -= can
    rem_s[s] -= can
    rem_d[c] -= can

greedy_cost = float(np.dot(greedy_flow, cost))
unmet = sum(rem_d.values())
print(f"Жадная стоимость: {greedy_cost:.4f}")
print(f"Неудовлетворённый спрос: {unmet:.6f}")
if base.success and unmet < 1e-6:
    gap = greedy_cost - base.fun
    print(f"Зазор к оптимуму: {gap:.4f} ({100 * gap / base.fun:.2f}%)")
elif unmet >= 1e-6:
    print("Жадный план не покрыл весь спрос (ограничения ёмкостей).")

pd.DataFrame({
    "from": [a[0] for a in arc_list],
    "to": [a[1] for a in arc_list],
    "greedy_flow": greedy_flow,
}).to_csv("greedy_flows.csv", index=False, encoding="utf-8-sig")
print("Сохранено: scenario_results.csv, shadow_prices.csv, greedy_flows.csv")
