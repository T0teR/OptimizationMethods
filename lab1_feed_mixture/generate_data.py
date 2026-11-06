
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 10213
N_PRODUCTS = 8

rng = np.random.default_rng(SEED)

products = [
    "Овёс",
    "Кукуруза",
    "Пшеница",
    "Пшеничные отруби",
    "Соевый шрот",
    "Подсолнечный шрот",
    "Люцерна",
    "Минеральная добавка"
]

# Базовые цены, руб./кг
base_prices = np.array([
    22, 18, 25, 16, 32, 21, 28, 40
])

# Базовые характеристики продуктов
base_nutrients = np.array([
    [0.12, 0.09, 0.13, 0.16, 0.44, 0.32, 0.18, 0.00],
    [11, 13, 12, 9, 10, 8, 7, 0],
    [0.10, 0.03, 0.04, 0.40, 0.12, 0.25, 0.30, 0],
    [0.001, 0.0003, 0.0005, 0.0013, 0.003, 0.002, 0.012, 0.20],
    [0.003, 0.0025, 0.0035, 0.010, 0.006, 0.008, 0.002, 0.08]
])

# Небольшие случайные отклонения
prices = base_prices * rng.uniform(0.95, 1.05, N_PRODUCTS)

nutrients_matrix = base_nutrients * rng.uniform(
    0.95, 1.05, base_nutrients.shape
)

# Формируем таблицу
data = pd.DataFrame({
    "product": products,
    "price": prices,
    "protein": nutrients_matrix[0],
    "energy": nutrients_matrix[1],
    "fiber": nutrients_matrix[2],
    "calcium": nutrients_matrix[3],
    "phosphorus": nutrients_matrix[4]
})

# Эталонная смесь
reference_mix = np.array([
    1.5, 1.5, 1.0, 1.0,
    1.2, 1.2, 1.2, 0.4
])

# Матрица питательных веществ
A = nutrients_matrix

# Минимальные нормы
minimums = 0.85 * (A @ reference_mix)

requirements = pd.DataFrame({
    "nutrient": [
        "protein",
        "energy",
        "fiber",
        "calcium",
        "phosphorus"
    ],
    "minimum": minimums
})

# Сохранение
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

data.to_csv(
    output_dir / "products.csv",
    index=False,
    encoding="utf-8-sig"
)

requirements.to_csv(
    output_dir / "requirements.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Данные успешно сгенерированы!")
print("\nПродукты:")
print(data.round(5).to_string(index=False))

print("\nМинимальные нормы:")
print(requirements.round(5).to_string(index=False))

print("\nSeed:", SEED)
