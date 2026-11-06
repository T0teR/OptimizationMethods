import numpy as np
import pandas as pd
from scipy.optimize import linprog

# 1. Загружаем данные
products = pd.read_csv("data/products.csv")
requirements = pd.read_csv("data/requirements.csv")

# 2. Формируем исходные данные модели
nutrients = [
    "protein",
    "energy",
    "fiber",
    "calcium",
    "phosphorus"
]

# Цены продуктов
c = products["price"].to_numpy()

# Матрица содержания питательных веществ
# Строки — питательные вещества, столбцы — продукты
A = products[nutrients].to_numpy().T

# Минимальные нормы
b = (
    requirements
    .set_index("nutrient")
    .loc[nutrients, "minimum"]
    .to_numpy()
)

n_products = len(products)

# 3. Ограничения по питательным веществам
# linprog принимает ограничения вида A_ub @ x <= b_ub.
# Поэтому умножаем исходные неравенства на -1.
A_ub = -A
b_ub = -b

# 4. Ограничение на общий вес смеси
A_eq = np.ones((1, n_products))
b_eq = np.array([9.0])

# 5. Неотрицательность переменных
bounds = [(0, None)] * n_products

# 6. Решение задачи линейного программирования
result = linprog(
    c,
    A_ub=A_ub,
    b_ub=b_ub,
    A_eq=A_eq,
    b_eq=b_eq,
    bounds=bounds,
    method="highs"
)

# 7. Проверяем статус решения
print("Статус решения:", result.message)

# Сохраняем лог солвера
with open("solver_log.txt", "w", encoding="utf-8") as log:
    log.write("=== Лог решателя HiGHS (базовый сценарий) ===\n")
    log.write(f"message: {result.message}\n")
    log.write(f"success: {result.success}\n")
    log.write(f"status: {result.status}\n")
    log.write(f"fun: {result.fun}\n")
    log.write(f"nit: {getattr(result, 'nit', 'n/a')}\n")
    if result.success:
        log.write(f"x: {result.x.tolist()}\n")
    log.write("\nИнтерпретация: Optimal означает, что найдено допустимое "
              "решение и подтверждена оптимальность для заданной линейной модели.\n")

if result.success:
    x = result.x

    print("\nМинимальная стоимость смеси:",
          round(result.fun, 4), "руб.")

    # 8. Формируем таблицу решения
    solution = products[["product", "price"]].copy()
    solution["quantity_kg"] = x
    solution["cost"] = x * c

    print("\nОптимальный состав смеси:")
    print(solution.round(4).to_string(index=False))

    # 9. Независимая проверка с помощью NumPy
    actual_nutrients = A @ x

    check = pd.DataFrame({
        "nutrient": nutrients,
        "actual": actual_nutrients,
        "minimum": b,
        "satisfied": actual_nutrients >= b - 1e-7
    })

    print("\nПроверка ограничений:")
    print(check.round(5).to_string(index=False))

    print("\nОбщий вес смеси:", round(np.sum(x), 6), "кг")
    print("Проверка общего веса:",
          abs(np.sum(x) - 9) < 1e-7)

    # 10. Сохраняем результаты
    solution.to_csv(
        "solution.csv",
        index=False,
        encoding="utf-8-sig"
    )

    check.to_csv(
        "independent_check.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nРезультаты сохранены!")
    print("Лог солвера: solver_log.txt")

else:
    print("Не удалось найти оптимальное решение.")