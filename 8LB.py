import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def build_xor_distribution_table(sbox):
    """Строит таблицу распределения XOR для 4-битного S-блока."""
    size = 16
    table = [[0] * size for _ in range(size)]
    
    # Для каждой возможной входной разности (Delta X)
    for dx in range(size):
        # Для каждого возможного входного значения (X)
        for x in range(size):
            x_prime = x ^ dx
            # Вычисляем выходную разность (Delta Y)
            dy = sbox[x] ^ sbox[x_prime]
            table[dx][dy] += 1
            
    return table

def on_build():
    try:
        # Получаем S-блок из ввода
        sbox_str = sbox_entry.get()
        sbox = [int(x.strip()) for x in sbox_str.split(",")]
        
        if len(sbox) != 16:
            raise ValueError("S-блок должен содержать ровно 16 чисел.")
        
        if any(x < 0 or x > 15 for x in sbox):
            raise ValueError("Числа должны быть в диапазоне от 0 до 15.")
            
        # Строим таблицу
        dist_table = build_xor_distribution_table(sbox)
        
        # Вывод таблицы
        output = "Таблица распределения XOR (строки - Delta X, столбцы - Delta Y):\n\n"
        
        # Заголовок столбцов
        output += " ΔX\\ΔY |" + "".join(f"{i:3}" for i in range(16)) + "\n"
        output += "-------|" + "-" * (16 * 3) + "\n"
        
        for dx in range(16):
            output += f" {dx:5} |"
            for dy in range(16):
                val = dist_table[dx][dy]
                output += f"{val:3}"
            output += "\n"
            
        # Поиск наиболее вероятных разностей
        max_val = 0
        probable_diffs = []
        
        # Начинаем с dx=1, так как dx=0 всегда дает dy=0 с частотой 16
        for dx in range(1, 16):
            for dy in range(16):
                if dist_table[dx][dy] > max_val:
                    max_val = dist_table[dx][dy]
                    probable_diffs = [(dx, dy)]
                elif dist_table[dx][dy] == max_val:
                    probable_diffs.append((dx, dy))
                    
        output += "\n--- АНАЛИЗ ВЕРОЯТНОСТЕЙ ---\n"
        output += f"Максимальная частота (кроме Delta X=0): {max_val}\n"
        output += "Наиболее вероятные пары разностей (ΔX -> ΔY):\n"
        for dx, dy in probable_diffs:
            prob = max_val / 16.0
            output += f"  {dx:01x} -> {dy:01x} (Вероятность: {prob:.3f})\n"
            
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, output)
        
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создание GUI
root = tk.Tk()
root.title("ЛБ8: Дифференциальный криптоанализ (Вариант 3)")
root.geometry("700x550")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="Введите S-блок (16 чисел через запятую):").pack(pady=5, anchor=tk.W)
sbox_entry = ttk.Entry(main_frame, width=80)
sbox_entry.pack(pady=5)
# Пример S-блока (из DES или произвольный)
sbox_entry.insert(0, "14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7")

build_btn = ttk.Button(main_frame, text="Построить таблицу XOR", command=on_build)
build_btn.pack(pady=10)

ttk.Label(main_frame, text="Результат:").pack(pady=5, anchor=tk.W)
result_text = scrolledtext.ScrolledText(main_frame, width=80, height=22, font=("Courier New", 10))
result_text.pack(pady=5, fill=tk.BOTH, expand=True)

root.mainloop()
