import tkinter as tk
from tkinter import ttk, scrolledtext
import string

class ChineseRemainderTheoremApp:
    """Решение системы сравнений по Китайской теореме об остатках"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()
    
    def setup_ui(self):
        """Создать интерфейс для КТО"""
        # Фрейм для входных данных
        input_frame = ttk.LabelFrame(self.frame, text="Система сравнений", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # Поля для ввода
        self.remainders = []
        self.moduli = []
        
        for i in range(3):
            row_frame = ttk.Frame(input_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(row_frame, text=f"x ≡", width=5).pack(side=tk.LEFT)
            
            remainder = tk.Entry(row_frame, width=5, font=("Arial", 11))
            remainder.pack(side=tk.LEFT, padx=5)
            self.remainders.append(remainder)
            
            ttk.Label(row_frame, text="(mod", width=6).pack(side=tk.LEFT)
            
            modulus = tk.Entry(row_frame, width=5, font=("Arial", 11))
            modulus.pack(side=tk.LEFT, padx=5)
            self.moduli.append(modulus)
            
            ttk.Label(row_frame, text=")").pack(side=tk.LEFT)
        
        # Заполнить значениями по умолчанию
        defaults_a = [2, 3, 2]
        defaults_m = [3, 5, 7]
        for i in range(3):
            self.remainders[i].insert(0, str(defaults_a[i]))
            self.moduli[i].insert(0, str(defaults_m[i]))
        
        # Кнопка решения
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        
        solve_btn = ttk.Button(button_frame, text="Решить систему", 
                               command=self.solve_crt)
        solve_btn.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для результатов
        output_frame = ttk.LabelFrame(self.frame, text="Результат", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=12, 
                                                      font=("Courier", 10), 
                                                      wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def extended_gcd(self, a, b):
        """Расширенный алгоритм Евклида"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def mod_inverse(self, a, m):
        """Найти обратный элемент a по модулю m"""
        gcd, x, _ = self.extended_gcd(a % m, m)
        if gcd != 1:
            return None
        return (x % m + m) % m
    
    def solve_crt(self):
        """Решить систему по Китайской теореме об остатках"""
        self.output_text.delete(1.0, tk.END)
        
        try:
            # Получить входные данные
            remainders = [int(self.remainders[i].get()) for i in range(3)]
            moduli = [int(self.moduli[i].get()) for i in range(3)]
            
            # Проверка на положительность
            if any(m <= 0 for m in moduli):
                self.output_text.insert(tk.END, "Ошибка: модули должны быть положительными")
                return
            
            # Вычислить M
            M = 1
            for m in moduli:
                M *= m
            
            self.output_text.insert(tk.END, "КИТАЙСКАЯ ТЕОРЕМА ОБ ОСТАТКАХ\n")
            self.output_text.insert(tk.END, "=" * 50 + "\n\n")
            self.output_text.insert(tk.END, "Система сравнений:\n")
            for i in range(3):
                self.output_text.insert(tk.END, 
                    f"  x ≡ {remainders[i]} (mod {moduli[i]})\n")
            
            self.output_text.insert(tk.END, f"\nM = {' × '.join(map(str, moduli))} = {M}\n\n")
            
            # Вычислить каждый Mi и его обратный
            solution = 0
            for i in range(3):
                Mi = M // moduli[i]
                Mi_inv = self.mod_inverse(Mi, moduli[i])
                
                if Mi_inv is None:
                    self.output_text.insert(tk.END, 
                        f"Ошибка: M_{i+1} и m_{i+1} не взаимно просты")
                    return
                
                term = remainders[i] * Mi * Mi_inv
                solution += term
                
                self.output_text.insert(tk.END, 
                    f"a_{i+1} = {remainders[i]}, M_{i+1} = {Mi}, " +
                    f"M_{i+1}⁻¹ ≡ {Mi_inv} (mod {moduli[i]})\n")
                self.output_text.insert(tk.END, 
                    f"Слагаемое: {remainders[i]} × {Mi} × {Mi_inv} = {term}\n\n")
            
            # Найти минимальное неотрицательное решение
            x = solution % M
            
            self.output_text.insert(tk.END, "=" * 50 + "\n")
            self.output_text.insert(tk.END, f"x ≡ {solution} ≡ {x} (mod {M})\n\n")
            self.output_text.insert(tk.END, f"ОТВЕТ: x = {x}\n")
            
            # Проверка
            self.output_text.insert(tk.END, "\nПроверка:\n")
            for i in range(3):
                remainder = x % moduli[i]
                status = "✓" if remainder == remainders[i] else "✗"
                self.output_text.insert(tk.END, 
                    f"  {x} mod {moduli[i]} = {remainder} {status}\n")
        
        except ValueError:
            self.output_text.insert(tk.END, "Ошибка: введите целые числа")

class CaesarCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Криптоанализ и теория чисел")
        self.root.geometry("810x600")
        self.root.bind("<Control-c>", self.copy_selected)

        # Создать вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка 1: Шифр Цезаря
        caesar_frame = ttk.Frame(self.notebook)
        self.notebook.add(caesar_frame, text="Шифр Цезаря")
        self.setup_caesar(caesar_frame)
        
        # Вкладка 2: Китайская теорема об остатках
        crt_frame = ttk.Frame(self.notebook)
        self.notebook.add(crt_frame, text="КТО")
        self.crt_app = ChineseRemainderTheoremApp(crt_frame)
    
    def setup_caesar(self, parent):
        """Настроить интерфейс шифра Цезаря"""
        # Фрейм для ввода
        input_frame = ttk.LabelFrame(parent, text="Исходный текст", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.input_text = tk.Entry(input_frame, width=80, font=("Arial", 11))
        self.input_text.pack(fill=tk.BOTH)
        self.input_text.insert(0, "LWKLQNWKDWLVWUXH")
        
        # Кнопка преобразования
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10)
        
        self.transform_btn = ttk.Button(button_frame, text="Преобразовать", 
                                        command=self.transform_text)
        self.transform_btn.pack()
        
        # Фрейм для вывода
        output_frame = ttk.LabelFrame(parent, text="Все возможные сдвиги", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для текста и кнопки копирования
        text_button_frame = ttk.Frame(output_frame)
        text_button_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrolled text для результатов
        self.output_text = scrolledtext.ScrolledText(text_button_frame, height=20, 
                                                      font=("Courier", 10), 
                                                      wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Кнопка копирования
        copy_btn = ttk.Button(text_button_frame, text="Копировать", 
                             command=self.copy_text)
        copy_btn.pack(side=tk.RIGHT, padx=5)
        
    def caesar_encrypt(self, text, shift):
        """Зашифровка текста с заданным сдвигом"""
        result = []
        for char in text.upper():
            if char in string.ascii_uppercase:
                shifted = (ord(char) - ord('A') + shift) % 26
                result.append(chr(shifted + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def transform_text(self):
        """Выполнить криптоанализ"""
        ciphertext = self.input_text.get().strip().upper()
        
        if not ciphertext:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Пожалуйста, введите текст")
            return
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Исходный текст (шифртекст): {ciphertext}\n")
        self.output_text.insert(tk.END, f"Длина текста: {len(ciphertext)} символов\n")
        self.output_text.insert(tk.END, "=" * 70 + "\n\n")
        self.output_text.insert(tk.END, "Сдвиги до возврата к исходному тексту:\n\n")
        
        # Все возможные сдвиги (от 0 до 25)
        for shift in range(1, 26):
            encrypted = self.caesar_encrypt(ciphertext, shift)
            self.output_text.insert(tk.END, 
                f"Сдвиг {shift:2d}: {encrypted}\n")
            
            if encrypted == ciphertext:
                break
    
    def copy_text(self):
        """Копировать содержимое поля вывода в буфер обмена"""
        content = self.output_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
    
    def copy_selected(self, event=None):
        """Копировать выделенный текст в буфер обмена по Ctrl+C"""
        try:
            selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.root.update()
        except tk.TclError:
            content = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
        return "break"

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CaesarCipherApp(root)
    root.mainloop()