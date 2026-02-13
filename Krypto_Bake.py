import tkinter as tk
from tkinter import ttk, scrolledtext
import string

class CaesarCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Криптоанализ шифра Цезаря")
        self.root.geometry("800x600")
        self.root.bind("<Control-c>", self.copy_selected)
        
        # Фрейм для ввода
        input_frame = ttk.LabelFrame(root, text="Исходный текст", padding=10)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.input_text = tk.Entry(input_frame, width=80, font=("Arial", 11))
        self.input_text.pack(fill=tk.BOTH)
        self.input_text.insert(0, "LWKLQNWKDWLVWUXH")
        
        # Кнопка преобразования
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        
        self.transform_btn = ttk.Button(button_frame, text="Преобразовать", 
                                        command=self.transform_text)
        self.transform_btn.pack()
        
        # Фрейм для вывода
        output_frame = ttk.LabelFrame(root, text="Все возможные сдвиги", padding=10)
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
            # Если текст не выделен, копируем всё содержимое
            content = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
        return "break"  # Предотвращаем стандартное поведение

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CaesarCipherApp(root)
    root.mainloop()