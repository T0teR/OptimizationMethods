"""
★ п. 3. Elastic filter — диагностика несовместимости.
Делаем задачу заведомо несовместной (покрытие ≥ 3 при том, что
у части районов доступно только 2 кандидата), затем ищем
минимальное суммарное «ослабление» ограничений.
"""
import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds

sites = pd.read_csv("data/sites.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)
c = sites["cost"].to_numpy()
A = coverage.to_numpy().astype(float)
m, n = A.shape


req = 3.0
print("Макс. доступное покрытие по районам:", A.sum(axis=1).astype(int).tolist())
print("Районы с покрытием < 3:", 
      [coverage.index[i] for i in range(m) if A[i].sum() < 3])


hard = milp(
    c=c,
    constraints=LinearConstraint(A, np.full(m, req), np.full(m, np.inf)),
    bounds=Bounds(0, 1),
    integrality=np.ones(n),
    options={"disp": False},
)
print("\nЖёсткая задача (покрытие ≥ 3): success =", hard.success)


c_el = np.concatenate([np.zeros(n), np.ones(m)])
A_ub = np.hstack([-A, -np.eye(m)])
b_ub = -np.full(m, req)
A_ub2 = np.hstack([np.eye(n), np.zeros((n, m))])
b_ub2 = np.ones(n)
A_all = np.vstack([A_ub, A_ub2])
b_all = np.concatenate([b_ub, b_ub2])
bounds = [(0, None)] * (n + m)

el_lp = linprog(c_el, A_ub=A_all, b_ub=b_all, bounds=bounds, method="highs")
assert el_lp.success
y_el = el_lp.x[:n]
s_el = el_lp.x[n:]
print("\n=== ELASTIC FILTER (LP) ===")
print(f"Минимальное суммарное ослабление Σ s_i = {el_lp.fun:.6f}")
print("Смещения по районам (s_i > 0):")
for i, name in enumerate(coverage.index):
    if s_el[i] > 1e-8:
        print(f"  {name}: s={s_el[i]:.4f}, доступно кандидатов={int(A[i].sum())}, требуется={req}")

el_milp = milp(
    c=c_el,
    constraints=LinearConstraint(
        np.hstack([A, np.eye(m)]),
        np.full(m, req),
        np.full(m, np.inf),
    ),
    bounds=Bounds(0, np.concatenate([np.ones(n), np.full(m, req)])),
    integrality=np.concatenate([np.ones(n), np.zeros(m)]),
    options={"disp": False},
)
print("\n=== ELASTIC FILTER (MILP, y binary) ===")
print("success:", el_milp.success)
if el_milp.success:
    print(f"Σ s_i = {el_milp.fun:.6f}")
    s_m = el_milp.x[n:]
    print("Смещения:")
    for i, name in enumerate(coverage.index):
        if s_m[i] > 1e-8:
            print(f"  {name}: s={s_m[i]:.4f}")

pd.DataFrame({
    "district": coverage.index,
    "available_candidates": A.sum(axis=1).astype(int),
    "required": req,
    "slack_lp": s_el,
    "slack_milp": el_milp.x[n:] if el_milp.success else np.nan,
}).to_csv("star_elastic.csv", index=False, encoding="utf-8-sig")
print("\nСохранено: star_elastic.csv")
