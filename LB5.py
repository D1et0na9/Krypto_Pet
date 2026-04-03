"""
Лабораторная работа №5
Атака на малую экспоненту RSA (e = 3).

Если открытый текст m мал настолько, что m³ < n,
то шифртекст c = m^e mod n = m³ (без модульного приведения).
Достаточно извлечь кубический корень из c, чтобы восстановить m.
"""

import tkinter as tk
from tkinter import messagebox
import random
from math import gcd


# =====================================================
# Математические функции
# =====================================================

def is_prime(n, rounds=20):
    """Проверка числа на простоту (тест Миллера-Рабина)"""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False

    # Представляем n-1 = 2^s * d, где d нечётное
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Проверяем несколько случайных свидетелей
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False  # составное

    return True  # вероятно простое


def generate_prime(bits):
    """Генерация случайного простого числа заданной битовой длины"""
    while True:
        # Генерируем нечётное число нужной длины
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n


def integer_cube_root(n):
    """
    Целочисленное извлечение кубического корня методом Ньютона.
    Возвращает наибольшее целое x, такое что x³ <= n.
    """
    if n < 0:
        return -integer_cube_root(-n)
    if n == 0:
        return 0

    # Начальное приближение
    x = 1 << ((n.bit_length() + 2) // 3)

    while True:
        # Итерация Ньютона: x_new = (2*x + n/x²) / 3
        x_new = (2 * x + n // (x * x)) // 3
        if x_new >= x:
            break
        x = x_new

    return x


def generate_rsa_keys(bits=512):
    """
    Генерация ключей RSA с e = 3.
    bits — битовая длина каждого простого числа p и q.
    Возвращает (n, e, d, p, q).
    """
    e = 3

    while True:
        p = generate_prime(bits)
        # p должно быть не делимо на 3, т.е. gcd(p-1, 3) = 1
        if gcd(p - 1, e) != 1:
            continue

        q = generate_prime(bits)
        if q == p:
            continue
        if gcd(q - 1, e) != 1:
            continue

        n = p * q
        phi = (p - 1) * (q - 1)
        # Вычисляем закрытый ключ d = e^(-1) mod phi
        d = pow(e, -1, phi)
        return n, e, d, p, q


def text_to_int(text):
    """Преобразование строки в целое число (через байты UTF-8)"""
    return int.from_bytes(text.encode('utf-8'), 'big')


def int_to_text(number):
    """Преобразование целого числа обратно в строку"""
    length = (number.bit_length() + 7) // 8
    return number.to_bytes(length, 'big').decode('utf-8')


# =====================================================
# Графический интерфейс
# =====================================================

# --- Глобальные переменные для хранения ключей ---
current_keys = {
    'n': None, 'e': 3, 'd': None, 'p': None, 'q': None
}


def do_generate_keys():
    """Генерация новых ключей RSA"""
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, "Генерация ключей RSA (e=3)...\n")
    text_output.update()

    n, e, d, p, q = generate_rsa_keys(bits=512)
    current_keys['n'] = n
    current_keys['d'] = d
    current_keys['p'] = p
    current_keys['q'] = q

    result = "=== Ключи RSA сгенерированы ===\n\n"
    result += f"p = {p}\n\n"
    result += f"q = {q}\n\n"
    result += f"n = p * q = {n}\n"
    result += f"  (длина n: {n.bit_length()} бит)\n\n"
    result += f"e = {e}\n\n"
    result += f"d = {d}\n\n"
    result += "Ключи готовы. Введите сообщение и нажмите 'Атака'.\n"

    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state=tk.DISABLED)


def do_attack():
    """Шифрование и атака на малую экспоненту"""
    if current_keys['n'] is None:
        messagebox.showwarning("Ошибка", "Сначала сгенерируйте ключи!")
        return

    message = entry_message.get().strip()
    if not message:
        messagebox.showwarning("Ошибка", "Введите сообщение!")
        return

    n = current_keys['n']
    e = current_keys['e']

    # Преобразуем сообщение в число
    m = text_to_int(message)

    # Проверяем условие атаки: m³ < n
    m_cubed = m ** 3
    attack_possible = m_cubed < n

    # Шифрование: c = m^e mod n
    c = pow(m, e, n)

    result = "=== Шифрование RSA (e = 3) ===\n\n"
    result += f"Открытый текст:   \"{message}\"\n"
    result += f"m (как число):    {m}\n"
    result += f"  (длина m: {m.bit_length()} бит)\n\n"
    result += f"n (модуль RSA):   {n}\n"
    result += f"  (длина n: {n.bit_length()} бит)\n\n"
    result += f"Шифртекст c = m^3 mod n:\n"
    result += f"c = {c}\n\n"

    # Проверяем условие уязвимости
    result += "=== Проверка условия уязвимости ===\n\n"
    result += f"m³ < n ?  →  {attack_possible}\n"
    if attack_possible:
        result += "Условие выполнено: m³ < n, значит c = m³ (без mod).\n"
        result += "Модульное приведение не произошло!\n\n"
    else:
        result += "Условие НЕ выполнено: m³ >= n.\n"
        result += "Сообщение слишком длинное для данной атаки.\n"
        result += "Попробуйте более короткое сообщение.\n\n"
        text_output.config(state=tk.NORMAL)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, result)
        text_output.config(state=tk.DISABLED)
        return

    # === Атака: извлекаем кубический корень из c ===
    result += "=== Атака: извлечение кубического корня ===\n\n"
    result += "Злоумышленник знает только c и e = 3.\n"
    result += "Поскольку m³ < n, шифртекст c = m³ точно.\n"
    result += "Вычисляем m = ∛c методом Ньютона...\n\n"

    m_recovered = integer_cube_root(c)

    # Проверяем, что корень точный
    if m_recovered ** 3 == c:
        result += f"m_восст = {m_recovered}\n\n"
        result += "Проверка: m_восст³ == c ?  →  Да!\n\n"

        try:
            recovered_text = int_to_text(m_recovered)
            result += f"Восстановленное сообщение: \"{recovered_text}\"\n\n"

            if recovered_text == message:
                result += "Атака успешна! Сообщение полностью восстановлено.\n"
            else:
                result += "Ошибка: восстановленный текст не совпадает.\n"
        except Exception:
            result += "Ошибка декодирования восстановленного числа в текст.\n"
    else:
        result += "Ошибка: кубический корень не точный.\n"

    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state=tk.DISABLED)


def do_demo():
    """Демонстрация с примером из задания"""
    # Генерируем ключи если ещё нет
    if current_keys['n'] is None:
        do_generate_keys()

    # Вставляем демо-текст
    entry_message.delete(0, tk.END)
    entry_message.insert(0, "HELLO")

    # Запускаем атаку
    do_attack()


def do_manual_attack():
    """Атака по вручную введённому шифртексту c"""
    c_str = entry_cipher.get().strip()
    if not c_str:
        messagebox.showwarning("Ошибка", "Введите шифртекст c (число)!")
        return

    try:
        c = int(c_str)
    except ValueError:
        messagebox.showwarning("Ошибка", "Шифртекст должен быть целым числом!")
        return

    if c < 0:
        messagebox.showwarning("Ошибка", "Шифртекст должен быть положительным!")
        return

    result = "=== Атака на введённый шифртекст ===\n\n"
    result += f"Шифртекст c = {c}\n\n"
    result += "Предполагаем: e = 3, m³ < n, значит c = m³.\n"
    result += "Извлекаем кубический корень...\n\n"

    m_recovered = integer_cube_root(c)

    # Проверяем точность
    if m_recovered ** 3 == c:
        result += f"m = ∛c = {m_recovered}\n\n"
        result += "Проверка: m³ == c ?  →  Да! Корень точный.\n\n"

        try:
            recovered_text = int_to_text(m_recovered)
            result += f"Восстановленный текст: \"{recovered_text}\"\n"
        except Exception:
            result += "Не удалось декодировать число в текст (UTF-8).\n"
            result += f"Число m = {m_recovered}\n"
    else:
        result += f"Ближайший корень: {m_recovered}\n"
        result += f"  {m_recovered}³ = {m_recovered ** 3}\n"
        result += f"  Разница с c: {c - m_recovered ** 3}\n\n"
        result += "Кубический корень не является целым числом.\n"
        result += "Возможно, m³ >= n и произошло модульное приведение.\n"
        result += "В этом случае простое извлечение корня не сработает.\n"

    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state=tk.DISABLED)


def do_clear():
    """Очистить все поля"""
    entry_message.delete(0, tk.END)
    entry_cipher.delete(0, tk.END)
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.config(state=tk.DISABLED)


# --- Создание окна ---
root = tk.Tk()
root.title("Атака на малую экспоненту RSA (e = 3)")
root.resizable(False, False)

# --- Описание ---
desc_text = (
    "Атака на малую открытую экспоненту RSA.\n"
    "Если e = 3 и m³ < n, то шифртекст c = m³ без модульного приведения.\n"
    "Для восстановления m достаточно извлечь кубический корень из c."
)
tk.Label(root, text=desc_text, justify=tk.CENTER, wraplength=600,
         font=("Arial", 10)).pack(padx=10, pady=5)

# --- Рамка ввода ---
frame_input = tk.LabelFrame(root, text="Ввод данных", padx=10, pady=10)
frame_input.pack(padx=10, pady=5, fill=tk.X)

tk.Label(frame_input, text="Сообщение (текст):").grid(row=0, column=0, sticky=tk.W)
entry_message = tk.Entry(frame_input, width=50)
entry_message.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Шифртекст c (число):").grid(row=1, column=0, sticky=tk.W)
entry_cipher = tk.Entry(frame_input, width=50)
entry_cipher.grid(row=1, column=1, padx=5, pady=2)

# --- Рамка кнопок ---
frame_buttons = tk.Frame(root)
frame_buttons.pack(padx=10, pady=5)

tk.Button(frame_buttons, text="Генерация ключей",
          width=18, command=do_generate_keys).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Атака (из текста)",
          width=18, command=do_attack).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Атака (из числа c)",
          width=18, command=do_manual_attack).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Демо",
          width=10, command=do_demo).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Очистить",
          width=10, command=do_clear).pack(side=tk.LEFT, padx=3)

# --- Рамка вывода ---
frame_output = tk.LabelFrame(root, text="Результат", padx=10, pady=10)
frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

text_output = tk.Text(frame_output, width=80, height=25,
                      state=tk.DISABLED, font=("Consolas", 10))
scrollbar = tk.Scrollbar(frame_output, command=text_output.yview)
text_output.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# --- Запуск ---
root.mainloop()
