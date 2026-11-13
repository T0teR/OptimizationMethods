"""
Базовая MILP: set covering — минимум затрат на вышки при полном покрытии районов.
"""
import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds

sites = pd.read_csv("data/sites.csv")
districts = pd.read_csv("data/districts.csv")
coverage = pd.read_csv("data/coverage.csv", index_col=0)

site_names = sites["site"].tolist()
dist_names = districts["district"].tolist()
c = sites["cost"].to_numpy()
A = coverage.to_numpy().astype(float)
n = len(site_names)
m = len(dist_names)


constraints = LinearConstraint(A, np.ones(m), np.full(m, np.inf))
bounds = Bounds(0, 1)
integrality = np.ones(n)

milp_res = milp(c=c, constraints=constraints, bounds=bounds, integrality=integrality,
                options={"disp": False})

print("=== MILP ===")
print("Статус:", milp_res.message)
print("success:", milp_res.success)

with open("solver_log.txt", "w", encoding="utf-8") as f:
    f.write("=== HiGHS MILP (set covering) ===\n")
    f.write(f"message: {milp_res.message}\n")
    f.write(f"success: {milp_res.success}\n")
    f.write(f"status: {milp_res.status}\n")
    f.write(f"fun: {milp_res.fun}\n")
    if milp_res.success:
        f.write(f"x: {milp_res.x.tolist()}\n")

if not milp_res.success:
    raise SystemExit("MILP не решена")

y = milp_res.x
print(f"Минимальная стоимость: {milp_res.fun:.6f}")

sol = sites.copy()
sol["open"] = (y > 0.5).astype(int)
sol["y_raw"] = y
print("\nОткрытые вышки:")
print(sol[sol["open"] == 1][["site", "cost"]].to_string(index=False))
print(f"Число вышек: {int(sol['open'].sum())}")

sol.to_csv("solution.csv", index=False, encoding="utf-8-sig")


print("\n=== НЕЗАВИСИМАЯ ПРОВЕРКА ===")
opened = y > 0.5
cover_count = A @ opened
check = pd.DataFrame({
    "district": dist_names,
    "coverage_count": cover_count,
    "required": 1,
    "satisfied": cover_count >= 1 - 1e-9,
})
print(check.to_string(index=False))
all_ok = bool(check["satisfied"].all())
cost_recalc = float(c @ opened)
print(f"\nВсе районы покрыты: {all_ok}")
print(f"Стоимость пересчёт: {cost_recalc:.6f}")
print(f"Бинарность: {np.all((y < 1e-9) | (y > 1 - 1e-9))}")

check.to_csv("independent_check.csv", index=False, encoding="utf-8-sig")
print("Сохранено: solution.csv, independent_check.csv, solver_log.txt")


print("\n=== LP-РЕЛАКСАЦИЯ ===")
lp = linprog(c, A_ub=-A, b_ub=-np.ones(m), bounds=[(0, 1)] * n, method="highs")
print("LP success:", lp.success, "  cost:", round(lp.fun, 6) if lp.success else None)

if lp.success:
    gap = milp_res.fun - lp.fun
    print(f"Интегральный зазор: {gap:.6f} ({100 * gap / max(lp.fun, 1e-12):.2f}%)")
    lp_df = sites.copy()
    lp_df["y_lp"] = lp.x
    lp_df["y_milp"] = y
    print(lp_df[["site", "cost", "y_lp", "y_milp"]].round(4).to_string(index=False))
    lp_df.to_csv("lp_vs_milp.csv", index=False, encoding="utf-8-sig")
    with open("gap.txt", "w", encoding="utf-8") as f:
        f.write(f"LP cost: {lp.fun}\n")
        f.write(f"MILP cost: {milp_res.fun}\n")
        f.write(f"gap: {gap}\n")
        f.write(f"gap_percent: {100 * gap / max(lp.fun, 1e-12)}\n")
