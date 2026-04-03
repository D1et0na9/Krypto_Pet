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


# --- Вспомогательные функции для форматированного вывода ---

def out_clear():
    """Очистить поле вывода"""
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)

def out_finish():
    """Завершить вывод (заблокировать редактирование)"""
    text_output.config(state=tk.DISABLED)

def out_heading(text):
    """Вывести заголовок секции"""
    text_output.insert(tk.END, f"  {text}\n", "heading")
    text_output.insert(tk.END, "  " + "\u2500" * 60 + "\n", "separator")

def out_label(label, value):
    """Вывести пару 'подпись: значение'"""
    text_output.insert(tk.END, f"  {label}: ", "label")
    text_output.insert(tk.END, f"{value}\n", "value")

def out_text(text):
    """Вывести обычный текст с отступом"""
    text_output.insert(tk.END, f"  {text}\n")

def out_success(text):
    """Вывести текст-успех (зелёный)"""
    text_output.insert(tk.END, f"  {text}\n", "success")

def out_error(text):
    """Вывести текст-ошибку (красный)"""
    text_output.insert(tk.END, f"  {text}\n", "error")

def out_highlight(text):
    """Вывести выделенный текст (крупный, для результата)"""
    text_output.insert(tk.END, f"  {text}\n", "highlight")

def out_number(text):
    """Вывести большое число (мелким шрифтом, с переносом)"""
    text_output.insert(tk.END, f"    {text}\n", "number")

def out_blank():
    """Пустая строка-разделитель"""
    text_output.insert(tk.END, "\n")


# --- Обработчики кнопок ---

def do_generate_keys():
    """Генерация новых ключей RSA"""
    out_clear()
    text_output.insert(tk.END, "  Генерация ключей RSA (e=3)...\n", "label")
    text_output.update()

    n, e, d, p, q = generate_rsa_keys(bits=512)
    current_keys['n'] = n
    current_keys['d'] = d
    current_keys['p'] = p
    current_keys['q'] = q

    out_clear()
    out_heading("Сгенерированные ключи RSA")
    out_blank()
    out_label("p", "")
    out_number(str(p))
    out_blank()
    out_label("q", "")
    out_number(str(q))
    out_blank()
    out_label("n = p * q", f"({n.bit_length()} бит)")
    out_number(str(n))
    out_blank()
    out_label("e (открытая экспонента)", str(e))
    out_blank()
    out_label("d (закрытая экспонента)", "")
    out_number(str(d))
    out_blank()
    out_success("Ключи готовы. Введите сообщение и нажмите \"Атака\".")
    out_finish()


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
    attack_possible = m ** 3 < n

    # Шифрование: c = m^e mod n
    c = pow(m, e, n)

    out_clear()

    # --- Блок 1: Шифрование ---
    out_heading("Шифрование RSA (e = 3)")
    out_blank()
    out_label("Открытый текст", f"\"{message}\"")
    out_label("m (числовое представление)", f"{m}  ({m.bit_length()} бит)")
    out_label("n (модуль RSA)", f"{n.bit_length()} бит")
    out_blank()
    out_label("Шифртекст  c = m^3 mod n", "")
    out_number(str(c))
    out_blank()

    # --- Блок 2: Проверка условия ---
    out_heading("Проверка условия уязвимости")
    out_blank()
    if attack_possible:
        out_success("m^3 < n  --  Да!")
        out_text("Модульное приведение не произошло, c = m^3 точно.")
    else:
        out_error("m^3 < n  --  Нет! (m^3 >= n)")
        out_text("Сообщение слишком длинное для данной атаки.")
        out_text("Попробуйте более короткое сообщение.")
        out_finish()
        return
    out_blank()

    # --- Блок 3: Атака ---
    out_heading("Атака: извлечение кубического корня")
    out_blank()
    out_text("Злоумышленник знает только c и e = 3.")
    out_text("Поскольку c = m^3, вычисляем m = cbrt(c) методом Ньютона...")
    out_blank()

    m_recovered = integer_cube_root(c)

    if m_recovered ** 3 == c:
        out_label("Найденный корень m", str(m_recovered))
        out_success("Проверка: m^3 == c  --  Совпадает!")
        out_blank()

        try:
            recovered_text = int_to_text(m_recovered)
            out_heading("Результат атаки")
            out_blank()
            out_highlight(f"Восстановленное сообщение:  \"{recovered_text}\"")
            out_blank()
            if recovered_text == message:
                out_success("Атака успешна! Сообщение полностью восстановлено.")
            else:
                out_error("Восстановленный текст не совпадает с исходным.")
        except Exception:
            out_error("Ошибка декодирования числа в текст.")
    else:
        out_error("Кубический корень не является целым числом.")

    out_finish()


def do_demo():
    """Демонстрация с примером из задания"""
    if current_keys['n'] is None:
        do_generate_keys()

    entry_message.delete(0, tk.END)
    entry_message.insert(0, "HELLO")
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

    out_clear()

    out_heading("Атака на введённый шифртекст")
    out_blank()
    out_label("Шифртекст c", "")
    out_number(str(c))
    out_blank()
    out_text("Предполагаем: e = 3, m^3 < n, значит c = m^3.")
    out_text("Извлекаем кубический корень...")
    out_blank()

    m_recovered = integer_cube_root(c)

    if m_recovered ** 3 == c:
        out_label("m = cbrt(c)", str(m_recovered))
        out_success("Проверка: m^3 == c  --  Совпадает!")
        out_blank()

        try:
            recovered_text = int_to_text(m_recovered)
            out_heading("Результат")
            out_blank()
            out_highlight(f"Восстановленный текст:  \"{recovered_text}\"")
        except Exception:
            out_text("Не удалось декодировать число в текст (UTF-8).")
            out_label("Число m", str(m_recovered))
    else:
        out_label("Ближайший корень", str(m_recovered))
        out_label("Корень^3", str(m_recovered ** 3))
        out_label("Разница с c", str(c - m_recovered ** 3))
        out_blank()
        out_error("Кубический корень не является целым числом.")
        out_text("Возможно, m^3 >= n и произошло модульное приведение.")
        out_text("В этом случае простое извлечение корня не сработает.")

    out_finish()


def do_clear():
    """Очистить все поля"""
    entry_message.delete(0, tk.END)
    entry_cipher.delete(0, tk.END)
    out_clear()
    out_finish()


# --- Создание окна ---
root = tk.Tk()
root.title("Атака на малую экспоненту RSA (e = 3)")
root.resizable(False, False)
root.configure(bg="#f5f5f5")

# --- Описание ---
desc_text = (
    "Атака на малую открытую экспоненту RSA.\n"
    "Если e = 3 и m\u00b3 < n, то шифртекст c = m\u00b3 без модульного приведения.\n"
    "Для восстановления m достаточно извлечь кубический корень из c."
)
tk.Label(root, text=desc_text, justify=tk.CENTER, wraplength=600,
         font=("Arial", 10), bg="#f5f5f5").pack(padx=10, pady=5)

# --- Рамка ввода ---
frame_input = tk.LabelFrame(root, text="Ввод данных", padx=10, pady=10,
                            font=("Arial", 10, "bold"), bg="#f5f5f5")
frame_input.pack(padx=10, pady=5, fill=tk.X)

tk.Label(frame_input, text="Сообщение (текст):", bg="#f5f5f5").grid(
    row=0, column=0, sticky=tk.W)
entry_message = tk.Entry(frame_input, width=50, font=("Consolas", 10))
entry_message.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Шифртекст c (число):", bg="#f5f5f5").grid(
    row=1, column=0, sticky=tk.W)
entry_cipher = tk.Entry(frame_input, width=50, font=("Consolas", 10))
entry_cipher.grid(row=1, column=1, padx=5, pady=2)

# --- Рамка кнопок ---
frame_buttons = tk.Frame(root, bg="#f5f5f5")
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
frame_output = tk.LabelFrame(root, text="Результат", padx=10, pady=10,
                             font=("Arial", 10, "bold"), bg="#f5f5f5")
frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

text_output = tk.Text(frame_output, width=80, height=25,
                      state=tk.DISABLED, font=("Consolas", 10),
                      bg="#1e1e2e", fg="#cdd6f4", insertbackground="#cdd6f4",
                      selectbackground="#45475a", relief=tk.FLAT, padx=5, pady=5,
                      wrap=tk.WORD)
scrollbar = tk.Scrollbar(frame_output, command=text_output.yview)
text_output.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# --- Настройка тегов для форматирования ---
text_output.tag_configure("heading", font=("Consolas", 11, "bold"),
                          foreground="#89b4fa")
text_output.tag_configure("separator", foreground="#585b70")
text_output.tag_configure("label", foreground="#a6adc8",
                          font=("Consolas", 10, "bold"))
text_output.tag_configure("value", foreground="#cdd6f4")
text_output.tag_configure("number", foreground="#f9e2af",
                          font=("Consolas", 9))
text_output.tag_configure("success", foreground="#a6e3a1",
                          font=("Consolas", 10, "bold"))
text_output.tag_configure("error", foreground="#f38ba8",
                          font=("Consolas", 10, "bold"))
text_output.tag_configure("highlight", foreground="#f5c2e7",
                          font=("Consolas", 12, "bold"))

# --- Запуск ---
root.mainloop()