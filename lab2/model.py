"""
Базовая LP-модель транзитной транспортной задачи.
Решатель: HiGHS через scipy.optimize.linprog
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from pathlib import Path

nodes = pd.read_csv("data/nodes.csv")
arcs = pd.read_csv("data/arcs.csv")

sources = nodes[nodes["type"] == "source"]["node"].tolist()
hubs = nodes[nodes["type"] == "hub"]["node"].tolist()
consumers = nodes[nodes["type"] == "consumer"]["node"].tolist()
all_nodes = nodes["node"].tolist()

supply = nodes.set_index("node")["supply"].to_dict()
demand = nodes.set_index("node")["demand"].to_dict()

arc_list = list(zip(arcs["from"], arcs["to"]))
n_arcs = len(arc_list)
cost = arcs["cost"].to_numpy()
cap = arcs["capacity"].to_numpy()

arc_idx = {a: i for i, a in enumerate(arc_list)}


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


result = linprog(
    cost,
    A_eq=A_eq,
    b_eq=b_eq,
    bounds=bounds,
    method="highs",
)

print("Статус:", result.message)
print("success:", result.success)

with open("solver_log.txt", "w", encoding="utf-8") as f:
    f.write("=== HiGHS base run (Lab 2) ===\n")
    f.write(f"message: {result.message}\n")
    f.write(f"success: {result.success}\n")
    f.write(f"status: {result.status}\n")
    f.write(f"fun: {result.fun}\n")
    f.write(f"nit: {getattr(result, 'nit', 'n/a')}\n")
    if result.success:
        f.write(f"x: {result.x.tolist()}\n")

if not result.success:
    print("Решение не найдено")
    raise SystemExit(1)

x = result.x
print(f"\nМинимальная стоимость перевозок: {result.fun:.6f}")

flow_df = arcs.copy()
flow_df["flow"] = x
flow_df["cost_total"] = flow_df["flow"] * flow_df["cost"]
flow_df = flow_df[flow_df["flow"] > 1e-8].sort_values("flow", ascending=False)

print("\nНенулевые потоки:")
print(flow_df.round(4).to_string(index=False))

flow_df.to_csv("solution_flows.csv", index=False, encoding="utf-8-sig")
print("\nСохранено: solution_flows.csv, solver_log.txt")


print("\n=== НЕЗАВИСИМАЯ ПРОВЕРКА ===")

def node_balance(node):
    inflow = 0.0
    outflow = 0.0
    for j, (fr, to) in enumerate(arc_list):
        if to == node:
            inflow += x[j]
        if fr == node:
            outflow += x[j]
    return inflow, outflow

checks = []
ok = True
for s in sources:
    inflow, outflow = node_balance(s)
    diff = abs(outflow - supply[s])
    checks.append({"node": s, "type": "source", "inflow": inflow, "outflow": outflow,
                   "target": supply[s], "ok": diff < 1e-6})
    if diff >= 1e-6:
        ok = False

for c in consumers:
    inflow, outflow = node_balance(c)
    diff = abs(inflow - demand[c])
    checks.append({"node": c, "type": "consumer", "inflow": inflow, "outflow": outflow,
                   "target": demand[c], "ok": diff < 1e-6})
    if diff >= 1e-6:
        ok = False

for h in hubs:
    inflow, outflow = node_balance(h)
    diff = abs(inflow - outflow)
    checks.append({"node": h, "type": "hub", "inflow": inflow, "outflow": outflow,
                   "target": 0.0, "ok": diff < 1e-6})
    if diff >= 1e-6:
        ok = False

cap_ok = True
for j, (fr, to) in enumerate(arc_list):
    if x[j] < -1e-8 or x[j] > cap[j] + 1e-8:
        cap_ok = False
        print(f"Нарушение ёмкости {fr}->{to}: flow={x[j]:.4f}, cap={cap[j]}")

check_df = pd.DataFrame(checks)
print(check_df.round(5).to_string(index=False))
print(f"\nБалансы узлов OK: {ok}")
print(f"Ёмкости дуг OK: {cap_ok}")
print(f"Стоимость пересчёт: {(x * cost).sum():.6f}")

check_df.to_csv("independent_check.csv", index=False, encoding="utf-8-sig")
print("Сохранено: independent_check.csv")
