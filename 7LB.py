import tkinter as tk
from tkinter import ttk, scrolledtext
import hashlib

def calculate_hmac_steps(key, message):
    """Вычисляет HMAC-SHA256 пошагово."""
    block_size = 64  # Размер блока для SHA-256 в байтах
    
    # Конвертируем входные данные в байты
    key_bytes = key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    
    steps = []
    
    # 1. Подготовка ключа
    steps.append(f"Исходный ключ: {key}")
    if len(key_bytes) > block_size:
        key_bytes = hashlib.sha256(key_bytes).digest()
        steps.append(f"Ключ длиннее {block_size} байт, хешируем его: {key_bytes.hex()}")
    
    if len(key_bytes) < block_size:
        key_bytes = key_bytes.ljust(block_size, b'\0')
        steps.append(f"Дополняем ключ нулевыми байтами до {block_size} байт:")
        steps.append(key_bytes.hex())
    
    # 2. Создание ipad и opad
    ipad = bytes([b ^ 0x36 for b in key_bytes])
    opad = bytes([b ^ 0x5c for b in key_bytes])
    
    steps.append("\n2. Вычисляем ipad (key XOR 0x36):")
    steps.append(ipad.hex())
    steps.append("\n3. Вычисляем opad (key XOR 0x5c):")
    steps.append(opad.hex())
    
    # 3. Внутренний хеш
    inner_data = ipad + message_bytes
    inner_hash = hashlib.sha256(inner_data).digest()
    steps.append("\n4. Внутренний хеш SHA256(ipad + message):")
    steps.append(inner_hash.hex())
    
    # 4. Внешний хеш (результат)
    outer_data = opad + inner_hash
    final_hmac = hashlib.sha256(outer_data).hexdigest()
    steps.append("\n5. Итоговый HMAC SHA256(opad + inner_hash):")
    steps.append(final_hmac)
    
    explanation = (
        "\n--- ТЕОРЕТИЧЕСКАЯ СПРАВКА ---\n"
        "Почему HMAC устойчив к атаке на удлинение (Length Extension Attack):\n"
        "В обычных хеш-функциях типа SHA-256 результат H(M) является состоянием функции.\n"
        "Зная H(M) и длину M, атакующий может продолжить хеширование, добавив свои данные.\n"
        "HMAC использует конструкцию H(K_out || H(K_in || M)). Внешнее хеширование\n"
        "скрывает внутреннее состояние хеш-функции от сообщения M, поэтому атакующий\n"
        "не может просто продолжить вычисление хеша, не зная внешнего ключа K_out."
    )
    steps.append(explanation)
    
    return final_hmac, "\n".join(steps)

def on_calculate():
    key = key_entry.get()
    message = msg_entry.get()
    
    if not key or not message:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Ошибка: введите ключ и сообщение!")
        return
        
    final_val, steps_str = calculate_hmac_steps(key, message)
    
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, steps_str)

# Создание GUI
root = tk.Tk()
root.title("ЛБ7: HMAC-SHA256 (Вариант 3)")
root.geometry("600x500")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="Сообщение:").grid(row=0, column=0, sticky=tk.W, pady=5)
msg_entry = ttk.Entry(main_frame, width=50)
msg_entry.grid(row=0, column=1, pady=5, padx=5)
msg_entry.insert(0, "Hello, world!")

ttk.Label(main_frame, text="Ключ:").grid(row=1, column=0, sticky=tk.W, pady=5)
key_entry = ttk.Entry(main_frame, width=50)
key_entry.grid(row=1, column=1, pady=5, padx=5)
key_entry.insert(0, "secret_key")

calc_btn = ttk.Button(main_frame, text="Вычислить HMAC", command=on_calculate)
calc_btn.grid(row=2, column=0, columnspan=2, pady=10)

ttk.Label(main_frame, text="Этапы вычисления:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
result_text = scrolledtext.ScrolledText(main_frame, width=70, height=18)
result_text.grid(row=4, column=0, columnspan=2, pady=5)

root.mainloop()
