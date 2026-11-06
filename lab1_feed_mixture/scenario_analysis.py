
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# Загружаем данные
products = pd.read_csv("data/products.csv")
requirements = pd.read_csv("data/requirements.csv")

nutrients = [
    "protein",
    "energy",
    "fiber",
    "calcium",
    "phosphorus"
]

c = products["price"].to_numpy()
A = products[nutrients].to_numpy().T

b = (
    requirements
    .set_index("nutrient")
    .loc[nutrients, "minimum"]
    .to_numpy()
)

n = len(products)

A_ub = -A
A_eq = np.ones((1, n))
b_eq = np.array([9.0])
bounds = [(0, None)] * n


def solve_model(requirements_vector):
    return linprog(
        c,
        A_ub=A_ub,
        b_ub=-requirements_vector,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )


# 1. Базовый сценарий
base = solve_model(b)

# 2. Дефицитный сценарий: нормы увеличиваются на 20%
deficit = solve_model(b * 1.2)

# 3. Стрессовый сценарий: нормы увеличиваются на 40%
stress = solve_model(b * 1.4)


# Сравнение сценариев
scenarios = [
    ("Базовый", base),
    ("Дефицитный (+20%)", deficit),
    ("Стрессовый (+40%)", stress)
]

rows = []

for name, result in scenarios:
    if result.success:
        rows.append({
            "scenario": name,
            "status": "Оптимальное решение",
            "cost": result.fun,
            "total_mass": np.sum(result.x)
        })
    else:
        rows.append({
            "scenario": name,
            "status": "Решение не найдено",
            "cost": np.nan,
            "total_mass": np.nan
        })

scenario_table = pd.DataFrame(rows)

print("СРАВНЕНИЕ СЦЕНАРИЕВ")
print(scenario_table.to_string(index=False))

scenario_table.to_csv(
    "scenario_results.csv",
    index=False,
    encoding="utf-8-sig"
)


# Анализ теневых цен базового решения
if base.success:
    shadow_prices = -base.ineqlin.marginals

    shadow_table = pd.DataFrame({
        "nutrient": nutrients,
        "minimum": b,
        "shadow_price": shadow_prices
    })

    print("\nТЕНЕВЫЕ ЦЕНЫ")
    print(shadow_table.round(6).to_string(index=False))

    print(
        "\nТеневая цена ограничения общего веса:",
        base.eqlin.marginals[0]
    )

    shadow_table.to_csv(
        "shadow_prices.csv",
        index=False,
        encoding="utf-8-sig"
    )
