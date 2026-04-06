import tkinter as tk
from tkinter import scrolledtext


# === Параметры эллиптической кривой y² = x³ + 2x + 3 mod 17 ===
A = 2   # коэффициент a
B = 3   # коэффициент b
P = 17  # модуль поля


def mod_inverse(a, p):
    """Нахождение обратного элемента по модулю p (расширенный алгоритм Евклида)"""
    if a < 0:
        a = a % p
    g, x, _ = extended_gcd(a, p)
    if g != 1:
        return None  # обратного элемента не существует
    return x % p


def extended_gcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def point_double(x1, y1, a, p):
    """
    Удвоение точки на эллиптической кривой.
    Возвращает координаты 2P и список шагов вычислений.
    """
    steps = []

    steps.append(f"Дана точка P = ({x1}, {y1})")
    steps.append(f"Кривая: y² = x³ + {a}x + {B} mod {p}")
    steps.append("")
    steps.append("=== Шаг 1: Вычисление λ ===")
    steps.append(f"λ = (3·x₁² + a) / (2·y₁) mod {p}")

    # Числитель: 3*x1^2 + a
    numerator = (3 * x1 * x1 + a) % p
    steps.append(f"Числитель = 3·{x1}² + {a} = 3·{x1*x1} + {a} = {3*x1*x1 + a} ≡ {numerator} (mod {p})")

    # Знаменатель: 2*y1
    denominator = (2 * y1) % p
    steps.append(f"Знаменатель = 2·{y1} = {2*y1} ≡ {denominator} (mod {p})")

    # Обратный элемент знаменателя
    inv_denom = mod_inverse(denominator, p)
    steps.append(f"Обратный элемент {denominator}⁻¹ mod {p} = {inv_denom}")
    steps.append(f"  (проверка: {denominator} · {inv_denom} = {denominator * inv_denom} ≡ {(denominator * inv_denom) % p} (mod {p}))")

    # Лямбда
    lam = (numerator * inv_denom) % p
    steps.append(f"λ = {numerator} · {inv_denom} = {numerator * inv_denom} ≡ {lam} (mod {p})")

    steps.append("")
    steps.append("=== Шаг 2: Вычисление координат 2P ===")

    # x3 = λ² - 2*x1 mod p
    x3 = (lam * lam - 2 * x1) % p
    steps.append(f"x₃ = λ² - 2·x₁ mod {p}")
    steps.append(f"x₃ = {lam}² - 2·{x1} = {lam*lam} - {2*x1} = {lam*lam - 2*x1} ≡ {x3} (mod {p})")

    # y3 = λ*(x1 - x3) - y1 mod p
    y3 = (lam * (x1 - x3) - y1) % p
    steps.append(f"y₃ = λ·(x₁ - x₃) - y₁ mod {p}")
    steps.append(f"y₃ = {lam}·({x1} - {x3}) - {y1} = {lam}·{(x1 - x3) % p} - {y1} = {lam * ((x1 - x3) % p) - y1} ≡ {y3} (mod {p})")

    steps.append("")
    steps.append(f"Результат: 2P = ({x3}, {y3})")

    steps.append("")
    steps.append("=== Шаг 3: Проверка результата ===")
    steps.append(f"Подставим ({x3}, {y3}) в уравнение кривой:")

    # Проверка: y3^2 mod p == (x3^3 + a*x3 + b) mod p
    left = (y3 * y3) % p
    right = (x3 * x3 * x3 + a * x3 + B) % p
    steps.append(f"Левая часть:  y² = {y3}² = {y3*y3} ≡ {left} (mod {p})")
    steps.append(f"Правая часть: x³ + {a}x + {B} = {x3}³ + {a}·{x3} + {B} = {x3**3} + {a*x3} + {B} = {x3**3 + a*x3 + B} ≡ {right} (mod {p})")

    if left == right:
        steps.append(f"✓ Левая часть ({left}) = Правая часть ({right}). Точка лежит на кривой!")
    else:
        steps.append(f"✗ Ошибка! {left} ≠ {right}. Точка НЕ лежит на кривой!")

    # Также проверим, что исходная точка лежит на кривой
    steps.append("")
    steps.append("=== Дополнительно: проверка исходной точки P ===")
    left_p = (y1 * y1) % p
    right_p = (x1 * x1 * x1 + a * x1 + B) % p
    steps.append(f"P({x1}, {y1}): {y1}² mod {p} = {left_p}, {x1}³ + {a}·{x1} + {B} mod {p} = {right_p}")
    if left_p == right_p:
        steps.append(f"✓ Точка P({x1}, {y1}) лежит на кривой.")
    else:
        steps.append(f"✗ Точка P({x1}, {y1}) НЕ лежит на кривой!")

    return x3, y3, steps


def run_calculation(output_widget):
    """Запуск вычислений и вывод результатов"""
    output_widget.config(state=tk.NORMAL)
    output_widget.delete("1.0", tk.END)

    # Точка P(2, 7) из условия задачи
    x1, y1 = 2, 7

    x3, y3, steps = point_double(x1, y1, A, P)

    for step in steps:
        output_widget.insert(tk.END, step + "\n")

    output_widget.config(state=tk.DISABLED)


def create_gui():
    """Создание графического интерфейса"""
    root = tk.Tk()
    root.title("Лабораторная №6 — Удвоение точки на эллиптической кривой (Вариант 3)")
    root.geometry("750x620")
    root.resizable(True, True)

    # Заголовок
    title_label = tk.Label(
        root,
        text="Удвоение точки на эллиптической кривой",
        font=("Arial", 14, "bold")
    )
    title_label.pack(pady=(10, 5))

    # Информация о задаче
    info_frame = tk.LabelFrame(root, text="Условие задачи (Вариант 3)", padx=10, pady=5)
    info_frame.pack(fill=tk.X, padx=10, pady=5)

    info_text = (
        "Кривая: y² = x³ + 2x + 3 mod 17\n"
        "Точка P = (2, 7)\n"
        "Задача: вычислить 2P, используя формулу удвоения λ = (3x₁² + a)/(2y₁) mod 17"
    )
    info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 11))
    info_label.pack(anchor=tk.W)

    # Кнопка вычисления
    calc_button = tk.Button(
        root,
        text="Вычислить 2P",
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        command=lambda: run_calculation(output_text)
    )
    calc_button.pack(pady=10)

    # Поле вывода результатов
    output_frame = tk.LabelFrame(root, text="Пошаговое решение", padx=10, pady=5)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    output_text = scrolledtext.ScrolledText(
        output_frame,
        wrap=tk.WORD,
        font=("Consolas", 11),
        state=tk.DISABLED
    )
    output_text.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
