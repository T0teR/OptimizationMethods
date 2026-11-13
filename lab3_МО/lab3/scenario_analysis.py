"""
Сценарии:
1) Базовый
2) Дефицитный: стоимость открытия всех вышек +20%
3) Стрессовый: каждый район должен быть покрыт ≥ 2 вышками
+ жадная эвристика
"""
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

sites = pd.read_csv("data/sites.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)
c = sites["cost"].to_numpy()
A = coverage.to_numpy().astype(float)
n = len(c)
m = A.shape[0]


def solve(cost_vec, cover_req):
    cons = LinearConstraint(A, np.full(m, cover_req), np.full(m, np.inf))
    res = milp(
        c=cost_vec,
        constraints=cons,
        bounds=Bounds(0, 1),
        integrality=np.ones(n),
        options={"disp": False},
    )
    return res


base = solve(c, 1.0)
print("Базовый: success =", base.success, " cost =", round(base.fun, 4) if base.success else None)


deficit = solve(c * 1.2, 1.0)
print("Дефицит (+20% к cost): success =", deficit.success,
      " cost =", round(deficit.fun, 4) if deficit.success else None)


stress = solve(c, 2.0)
print("Стресс (покрытие ≥2): success =", stress.success,
      " cost =", round(stress.fun, 4) if stress.success else None)

rows = []
for name, res in [
    ("Базовый", base),
    ("Дефицит cost+20%", deficit),
    ("Стресс покрытие≥2", stress),
]:
    opened = int(np.sum(res.x > 0.5)) if res.success else None
    rows.append({
        "scenario": name,
        "status": "Optimal" if res.success else "Infeasible/Fail",
        "cost": res.fun if res.success else np.nan,
        "towers_open": opened,
    })
scen = pd.DataFrame(rows)
print("\n", scen.to_string(index=False))
scen.to_csv("scenario_results.csv", index=False, encoding="utf-8-sig")


print("\n=== ЖАДНАЯ ЭВРИСТИКА ===")
uncovered = set(range(m))
chosen = []
rem_cost = 0.0
A_bool = A.astype(bool)

while uncovered:
    best_j, best_score = None, -1.0
    for j in range(n):
        if j in chosen:
            continue
        newly = sum(1 for i in uncovered if A_bool[i, j])
        if newly == 0:
            continue
        score = newly / c[j]
        if score > best_score:
            best_score = score
            best_j = j
    if best_j is None:
        print("Жадный алгоритм не смог покрыть все районы")
        break
    chosen.append(best_j)
    rem_cost += c[best_j]
    uncovered = {i for i in uncovered if not A_bool[i, best_j]}

print(f"Жадные вышки: {[sites.loc[j, 'site'] for j in chosen]}")
print(f"Жадная стоимость: {rem_cost:.4f}")
if base.success:
    gap = rem_cost - base.fun
    print(f"Зазор к MILP: {gap:.4f} ({100 * gap / base.fun:.2f}%)")

pd.DataFrame({
    "site": [sites.loc[j, "site"] for j in chosen],
    "cost": [c[j] for j in chosen],
}).to_csv("greedy_solution.csv", index=False, encoding="utf-8-sig")
print("Сохранено: scenario_results.csv, greedy_solution.csv")
