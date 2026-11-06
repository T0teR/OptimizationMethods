
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# Загружаем исходные данные
products = pd.read_csv("data/products.csv")
requirements = pd.read_csv("data/requirements.csv")

nutrients = [
    "protein",
    "energy",
    "fiber",
    "calcium",
    "phosphorus"
]

A = products[nutrients].to_numpy().T

b = (
    requirements
    .set_index("nutrient")
    .loc[nutrients, "minimum"]
    .to_numpy()
)

n = len(products)

# Стрессовые требования: увеличение на 40%
stress_b = b * 1.4

# Ограничение на массу смеси
A_eq = np.ones((1, n))
b_eq = np.array([9.0])

bounds = [(0, None)] * n

print("СТРЕССОВЫЕ ТРЕБОВАНИЯ")
for name, value in zip(nutrients, stress_b):
    print(f"{name}: {value:.6f}")


# ------------------------------------------------
# 1. Максимально возможное содержание каждого
#    питательного вещества в смеси массой 9 кг
# ------------------------------------------------

print("\nМАКСИМАЛЬНО ДОСТИЖИМЫЕ ЗНАЧЕНИЯ")

max_rows = []

for i, name in enumerate(nutrients):

    # Максимизируем содержание одного вещества
    result = linprog(
        -A[i],
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )

    maximum = -result.fun

    max_rows.append({
        "nutrient": name,
        "stress_minimum": stress_b[i],
        "maximum_possible": maximum,
        "individually_feasible": maximum >= stress_b[i] - 1e-7
    })

max_table = pd.DataFrame(max_rows)

print(max_table.round(6).to_string(index=False))


# ------------------------------------------------
# 2. Проверка: что будет, если убрать по одному
#    ограничению из стрессового сценария
# ------------------------------------------------

print("\nПРОВЕРКА УДАЛЕНИЯ ОГРАНИЧЕНИЙ")

leave_one_out_rows = []

for i, name in enumerate(nutrients):

    # Оставляем все ограничения, кроме i-го
    mask = np.ones(len(nutrients), dtype=bool)
    mask[i] = False

    result = linprog(
        np.zeros(n),
        A_ub=-A[mask],
        b_ub=-stress_b[mask],
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )

    leave_one_out_rows.append({
        "removed_constraint": name,
        "solution_exists": result.success
    })

    print(
        f"Убрали {name}: "
        f"{'решение найдено' if result.success else 'решения нет'}"
    )

leave_one_out_table = pd.DataFrame(leave_one_out_rows)

# Сохраняем результаты
max_table.to_csv(
    "stress_maximums.csv",
    index=False,
    encoding="utf-8-sig"
)

leave_one_out_table.to_csv(
    "stress_leave_one_out.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nРезультаты сохранены!")






from itertools import combinations

print("\nПРОВЕРКА УДАЛЕНИЯ ПАР ОГРАНИЧЕНИЙ")

pair_rows = []

for first, second in combinations(range(len(nutrients)), 2):

    mask = np.ones(len(nutrients), dtype=bool)
    mask[[first, second]] = False

    result = linprog(
        np.zeros(n),
        A_ub=-A[mask],
        b_ub=-stress_b[mask],
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )

    removed = f"{nutrients[first]} + {nutrients[second]}"

    pair_rows.append({
        "removed_constraints": removed,
        "solution_exists": result.success
    })

    print(
        f"Убрали {removed}: "
        f"{'решение найдено' if result.success else 'решения нет'}"
    )

pair_table = pd.DataFrame(pair_rows)

pair_table.to_csv(
    "stress_pair_check.csv",
    index=False,
    encoding="utf-8-sig"
)






# Решение стрессовой задачи без ограничения по энергии

mask = np.array([
    name != "energy"
    for name in nutrients
])

result = linprog(
    np.zeros(n),
    A_ub=-A[mask],
    b_ub=-stress_b[mask],
    A_eq=A_eq,
    b_eq=b_eq,
    bounds=bounds,
    method="highs"
)

if result.success:
    x = result.x

    print("\nРЕШЕНИЕ БЕЗ ОГРАНИЧЕНИЯ ПО ЭНЕРГИИ")

    solution = pd.DataFrame({
        "product": products["product"],
        "quantity_kg": x
    })

    print(solution.round(5).to_string(index=False))

    actual = A @ x

    print("\nПроверка всех показателей:")
    for i, name in enumerate(nutrients):
        print(
            f"{name}: фактически {actual[i]:.6f}, "
            f"требуется {stress_b[i]:.6f}"
        )
else:
    print("Решение не найдено")
