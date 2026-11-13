"""
★ п. 10. Двойственная интерпретация LP-релаксации set covering.
Прямая LP:  min c'y,  A y >= 1,  0 <= y <= 1
Двойственная: max 1'π - 1'μ,  A'π - μ <= c,  π >= 0, μ >= 0
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog

sites = pd.read_csv("data/sites.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)
c = sites["cost"].to_numpy()
A = coverage.to_numpy().astype(float)
m, n = A.shape


A_ub = np.vstack([-A, np.eye(n)])
b_ub = np.concatenate([-np.ones(m), np.ones(n)])
primal = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * n, method="highs")
assert primal.success
print("=== ПРЯМАЯ LP ===")
print(f"Цель: {primal.fun:.6f}")


n_dual = m + n
c_dual = np.concatenate([-np.ones(m), np.ones(n)])  

A_dual = np.hstack([A.T, -np.eye(n)])
dual = linprog(c_dual, A_ub=A_dual, b_ub=c, bounds=[(0, None)] * n_dual, method="highs")
assert dual.success
dual_obj = -dual.fun 
print("\n=== ДВОЙСТВЕННАЯ ===")
print(f"Цель: {dual_obj:.6f}")
print(f"Разность |Z_primal - Z_dual|: {abs(primal.fun - dual_obj):.2e}")

pi = dual.x[:m]
mu = dual.x[m:]
print("\nНенулевые π (ценность покрытия района):")
for i, name in enumerate(coverage.index):
    if pi[i] > 1e-8:
        print(f"  {name}: {pi[i]:.6f}")

print("\nНенулевые μ (штраф за верхнюю границу y<=1):")
for j, name in enumerate(sites["site"]):
    if mu[j] > 1e-8:
        print(f"  {name}: {mu[j]:.6f}")

pd.DataFrame({"district": coverage.index, "pi": pi}).to_csv(
    "star_dual_pi.csv", index=False, encoding="utf-8-sig"
)
pd.DataFrame({"site": sites["site"], "mu": mu, "y_lp": primal.x}).to_csv(
    "star_dual_mu.csv", index=False, encoding="utf-8-sig"
)
print("\nСохранено: star_dual_pi.csv, star_dual_mu.csv")
print("Сильная двойственность выполняется." if abs(primal.fun - dual_obj) < 1e-8 else "Расхождение!")
