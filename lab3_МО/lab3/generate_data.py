"""
ЛР3, вариант 2: покрытие районов вышками связи (set covering).
20 районов, 12 кандидатов на размещение. Seed = 10213.
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 10213
rng = np.random.default_rng(SEED)

N_DISTRICTS = 20
N_SITES = 12

districts = [f"D{i+1}" for i in range(N_DISTRICTS)]
sites = [f"T{j+1}" for j in range(N_SITES)]
base_cost = np.array([12, 15, 10, 18, 14, 16, 11, 13, 17, 12, 15, 14], dtype=float)
cost = base_cost * rng.uniform(0.95, 1.05, size=N_SITES)
coverage = np.zeros((N_DISTRICTS, N_SITES), dtype=int)

for j in range(N_SITES):
    k = int(rng.integers(5, 10))
    chosen = rng.choice(N_DISTRICTS, size=k, replace=False)
    coverage[chosen, j] = 1

for i in range(N_DISTRICTS):
    if coverage[i].sum() < 2:
        extra = rng.choice(np.where(coverage[i] == 0)[0], size=2 - int(coverage[i].sum()), replace=False)
        coverage[i, extra] = 1

dist_xy = rng.uniform(0, 10, size=(N_DISTRICTS, 2))
site_xy = rng.uniform(0, 10, size=(N_SITES, 2))

Path("data").mkdir(exist_ok=True)

pd.DataFrame({
    "site": sites,
    "cost": cost.round(4),
    "x": site_xy[:, 0].round(4),
    "y": site_xy[:, 1].round(4),
}).to_csv("data/sites.csv", index=False, encoding="utf-8-sig")

pd.DataFrame({
    "district": districts,
    "x": dist_xy[:, 0].round(4),
    "y": dist_xy[:, 1].round(4),
}).to_csv("data/districts.csv", index=False, encoding="utf-8-sig")

cov_df = pd.DataFrame(coverage, index=districts, columns=sites)
cov_df.to_csv("data/coverage.csv", encoding="utf-8-sig")

print("Сайты:")
print(pd.read_csv("data/sites.csv").to_string(index=False))
print("\nПокрытие (1 = покрывает):")
print(cov_df.to_string())
print(f"\nМин. покрытие района: {coverage.sum(axis=1).min()}, макс.: {coverage.sum(axis=1).max()}")
print("Seed:", SEED)
print("Данные сохранены в data/")
