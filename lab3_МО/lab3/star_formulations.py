"""
★ п. 6. Сравнение двух MILP-формулировок одной задачи.
F1: классический set covering (только y_j)
F2: assignment-формулировка (x_ij + y_j): какой сайт покрывает какой район
Сравниваем LP-релаксации (силу) и время/статус MILP.
"""
import time
import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds

sites = pd.read_csv("data/sites.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)
c = sites["cost"].to_numpy()
A = coverage.to_numpy().astype(float)
m, n = A.shape



def solve_f1_lp():
    return linprog(c, A_ub=-A, b_ub=-np.ones(m), bounds=[(0, 1)] * n, method="highs")

def solve_f1_milp():
    return milp(
        c=c,
        constraints=LinearConstraint(A, np.ones(m), np.full(m, np.inf)),
        bounds=Bounds(0, 1),
        integrality=np.ones(n),
        options={"disp": False},
    )


pairs = [(i, j) for i in range(m) for j in range(n) if A[i, j] > 0.5]
n_x = len(pairs)


def build_f2():
    c2 = np.concatenate([c, np.zeros(n_x)])
    rows = []
    rhs_lo = []
    for i in range(m):
        row = np.zeros(n + n_x)
        for k, (ii, jj) in enumerate(pairs):
            if ii == i:
                row[n + k] = 1.0
        rows.append(row)
        rhs_lo.append(1.0)
    for k, (i, j) in enumerate(pairs):
        row = np.zeros(n + n_x)
        row[n + k] = 1.0
        row[j] = -1.0
        rows.append(row)
        rhs_lo.append(-np.inf) 
    A_eq = None
    A2 = np.vstack(rows)
    lo = np.concatenate([np.ones(m), np.full(n_x, -np.inf)])
    hi = np.concatenate([np.full(m, np.inf), np.zeros(n_x)])
    return c2, A2, lo, hi

c2, A2, lo2, hi2 = build_f2()

def solve_f2_lp():
    A_ub_list = []
    b_ub_list = []
    for i in range(m):
        A_ub_list.append(-A2[i])
        b_ub_list.append(-1.0)
    for k in range(len(pairs)):
        A_ub_list.append(A2[m + k])
        b_ub_list.append(0.0)
    n_tot = n + len(pairs)
    A_ub_list.append(np.eye(n_tot))
    b_ub_list.extend([1.0] * n_tot)
    A_ub = np.vstack(A_ub_list)
    b_ub = np.array(b_ub_list, dtype=float)
    return linprog(c2, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * n_tot, method="highs")

def solve_f2_milp():
    n_tot = n + len(pairs)
    return milp(
        c=c2,
        constraints=LinearConstraint(A2, lo2, hi2),
        bounds=Bounds(0, 1),
        integrality=np.ones(n_tot),
        options={"disp": False},
    )

print("=== F1: Set Covering ===")
t0 = time.perf_counter()
lp1 = solve_f1_lp()
t_lp1 = time.perf_counter() - t0
t0 = time.perf_counter()
milp1 = solve_f1_milp()
t_milp1 = time.perf_counter() - t0
print(f"LP:   success={lp1.success}, cost={lp1.fun:.6f}, time={t_lp1:.4f}s")
print(f"MILP: success={milp1.success}, cost={milp1.fun:.6f}, time={t_milp1:.4f}s")
gap1 = milp1.fun - lp1.fun if (lp1.success and milp1.success) else np.nan
print(f"Gap:  {gap1:.6f}")

print("\n=== F2: Assignment formulation ===")
t0 = time.perf_counter()
lp2 = solve_f2_lp()
t_lp2 = time.perf_counter() - t0
t0 = time.perf_counter()
milp2 = solve_f2_milp()
t_milp2 = time.perf_counter() - t0
print(f"LP:   success={lp2.success}, cost={lp2.fun:.6f}, time={t_lp2:.4f}s")
print(f"MILP: success={milp2.success}, cost={milp2.fun:.6f}, time={t_milp2:.4f}s")
gap2 = milp2.fun - lp2.fun if (lp2.success and milp2.success) else np.nan
print(f"Gap:  {gap2:.6f}")

print("\n=== Сравнение ===")
print(f"F1 LP cost = {lp1.fun:.6f}, F2 LP cost = {lp2.fun:.6f}")
print("Более сильная релаксация — та, у которой LP-bound выше (ближе к MILP).")
if lp1.success and lp2.success:
    if lp2.fun > lp1.fun + 1e-8:
        print("F2 сильнее F1")
    elif lp1.fun > lp2.fun + 1e-8:
        print("F1 сильнее F2")
    else:
        print("Релаксации одинаковой силы (на этом экземпляре)")

cmp = pd.DataFrame([
    {"formulation": "F1 set covering", "lp_cost": lp1.fun, "milp_cost": milp1.fun,
     "gap": gap1, "lp_time_s": t_lp1, "milp_time_s": t_milp1, "n_vars": n},
    {"formulation": "F2 assignment", "lp_cost": lp2.fun, "milp_cost": milp2.fun,
     "gap": gap2, "lp_time_s": t_lp2, "milp_time_s": t_milp2, "n_vars": n + len(pairs)},
])
print(cmp.round(6).to_string(index=False))
cmp.to_csv("star_formulations.csv", index=False, encoding="utf-8-sig")
print("\nСохранено: star_formulations.csv")
