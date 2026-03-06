import tkinter as tk
from tkinter import messagebox

# =====================================================
# Лабораторная работа №3, Вариант 3
# Шифр Белазо (автоключ)
# Ключевое слово: KING, текст: ATTACK
# =====================================================

# --- Алфавит (только заглавные английские буквы) ---
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = len(ALPHABET)  # 26


def char_to_num(ch):
    """Буква -> число (A=0, B=1, ..., Z=25)"""
    return ALPHABET.index(ch.upper())


def num_to_char(n):
    """Число -> буква"""
    return ALPHABET[n % MOD]


# --- Шифрование автоключом ---
def encrypt_autokey(plaintext, keyword):
    """
    Шифрование методом автоключа (шифр Белазо).
    После исчерпания ключевого слова в качестве ключа
    используются буквы самого открытого текста.
    Формула: C_i = (P_i + K_i) mod 26
    """
    plaintext = plaintext.upper()
    keyword = keyword.upper()

    # Формируем полный ключ: сначала ключевое слово, потом буквы открытого текста
    full_key = list(keyword)
    for ch in plaintext:
        full_key.append(ch)
    # Ключ обрезаем до длины текста
    full_key = full_key[:len(plaintext)]

    ciphertext = ""
    steps = []  # Для пошагового отображения

    for i, p_char in enumerate(plaintext):
        p = char_to_num(p_char)       # Номер буквы открытого текста
        k = char_to_num(full_key[i])  # Номер буквы ключа
        c = (p + k) % MOD             # Шифрование
        c_char = num_to_char(c)
        ciphertext += c_char

        # Сохраняем шаг для вывода
        source = "ключ" if i < len(keyword) else "откр.текст"
        steps.append(
            f"  Позиция {i+1}: {p_char}({p}) + {full_key[i]}({k}) [{source}] "
            f"= {c} mod {MOD} = {c_char}"
        )

    return ciphertext, full_key, steps


# --- Расшифрование автоключом ---
def decrypt_autokey(ciphertext, keyword):
    """
    Расшифрование методом автоключа.
    Ключ восстанавливается по мере расшифрования:
    каждая расшифрованная буква добавляется к ключу.
    Формула: P_i = (C_i - K_i) mod 26
    """
    ciphertext = ciphertext.upper()
    keyword = keyword.upper()

    # Начинаем с ключевого слова
    full_key = list(keyword)
    plaintext = ""
    steps = []

    for i, c_char in enumerate(ciphertext):
        c = char_to_num(c_char)       # Номер буквы шифртекста
        k = char_to_num(full_key[i])  # Номер буквы ключа
        p = (c - k) % MOD             # Расшифрование
        p_char = num_to_char(p)
        plaintext += p_char

        # Добавляем расшифрованную букву к ключу для следующих позиций
        full_key.append(p_char)

        source = "ключ" if i < len(keyword) else "откр.текст"
        steps.append(
            f"  Позиция {i+1}: {c_char}({c}) - {full_key[i]}({k}) [{source}] "
            f"= {p} mod {MOD} = {p_char}"
        )

    return plaintext, full_key[:len(ciphertext)], steps


# =====================================================
# Графический интерфейс (tkinter)
# =====================================================

def do_encrypt():
    """Обработчик кнопки 'Зашифровать'"""
    plaintext = entry_text.get().strip()
    keyword = entry_key.get().strip()

    if not plaintext or not keyword:
        messagebox.showwarning("Ошибка", "Введите текст и ключ!")
        return

    # Проверяем, что только английские буквы
    if not plaintext.isalpha() or not keyword.isalpha():
        messagebox.showwarning("Ошибка", "Допустимы только английские буквы!")
        return

    ciphertext, full_key, steps = encrypt_autokey(plaintext, keyword)

    # Формируем вывод
    result = f"Открытый текст:  {plaintext.upper()}\n"
    result += f"Ключевое слово:  {keyword.upper()}\n"
    result += f"Полный ключ:     {''.join(full_key)}\n"
    result += f"\nПошаговое шифрование:\n"
    result += "\n".join(steps)
    result += f"\n\nШифртекст:       {ciphertext}\n"

    # Выводим результат
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state=tk.DISABLED)


def do_decrypt():
    """Обработчик кнопки 'Расшифровать'"""
    ciphertext = entry_text.get().strip()
    keyword = entry_key.get().strip()

    if not ciphertext or not keyword:
        messagebox.showwarning("Ошибка", "Введите текст и ключ!")
        return

    if not ciphertext.isalpha() or not keyword.isalpha():
        messagebox.showwarning("Ошибка", "Допустимы только английские буквы!")
        return

    plaintext, full_key, steps = decrypt_autokey(ciphertext, keyword)

    result = f"Шифртекст:       {ciphertext.upper()}\n"
    result += f"Ключевое слово:  {keyword.upper()}\n"
    result += f"Полный ключ:     {''.join(full_key)}\n"
    result += f"\nПошаговое расшифрование:\n"
    result += "\n".join(steps)
    result += f"\n\nОткрытый текст:  {plaintext}\n"

    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    text_output.config(state=tk.DISABLED)


def do_demo():
    """Демонстрация из задания: ключ KING, текст ATTACK"""
    entry_text.delete(0, tk.END)
    entry_text.insert(0, "ATTACK")
    entry_key.delete(0, tk.END)
    entry_key.insert(0, "KING")
    do_encrypt()


def do_clear():
    """Очистить все поля"""
    entry_text.delete(0, tk.END)
    entry_key.delete(0, tk.END)
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.config(state=tk.DISABLED)


# --- Создание окна ---
root = tk.Tk()
root.title("Шифр Белазо (автоключ)")
root.resizable(False, False)

# --- Рамка ввода ---
frame_input = tk.LabelFrame(root, text="Ввод данных", padx=10, pady=10)
frame_input.pack(padx=10, pady=5, fill=tk.X)

tk.Label(frame_input, text="Текст:").grid(row=0, column=0, sticky=tk.W)
entry_text = tk.Entry(frame_input, width=40)
entry_text.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Ключ:").grid(row=1, column=0, sticky=tk.W)
entry_key = tk.Entry(frame_input, width=40)
entry_key.grid(row=1, column=1, padx=5, pady=2)

# --- Рамка кнопок ---
frame_buttons = tk.Frame(root)
frame_buttons.pack(padx=10, pady=5)

tk.Button(frame_buttons, text="Зашифровать", width=15, command=do_encrypt).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Расшифровать", width=15, command=do_decrypt).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Демо (ATTACK)", width=15, command=do_demo).pack(side=tk.LEFT, padx=3)
tk.Button(frame_buttons, text="Очистить", width=15, command=do_clear).pack(side=tk.LEFT, padx=3)

# --- Рамка вывода ---
frame_output = tk.LabelFrame(root, text="Результат", padx=10, pady=10)
frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

text_output = tk.Text(frame_output, width=60, height=16, state=tk.DISABLED, font=("Consolas", 10))
text_output.pack(fill=tk.BOTH, expand=True)

# --- Запуск ---
root.mainloop()
