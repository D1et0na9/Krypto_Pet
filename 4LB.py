"""
Лабораторная работа №4: Блочные шифры и режимы (DES/AES)
Вариант 3: Демонстрация уязвимости режима ECB на примере изображения.

Программа создаёт простое монохромное изображение с чёткими границами,
шифрует его в режимах ECB и CBC, и показывает результат —
в ECB визуальная структура сохраняется, в CBC — нет.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from Crypto.Cipher import AES
import os
import io


# === Функции для работы с изображениями и шифрованием ===

def create_test_image(width=256, height=256):
    """Создаём тестовое монохромное изображение с чёткими геометрическими фигурами"""
    img = Image.new('L', (width, height), 255)  # белый фон, градации серого
    draw = ImageDraw.Draw(img)

    # Рисуем чёрные прямоугольники и полосы — области с повторяющимися пикселями
    draw.rectangle([30, 30, 100, 100], fill=0)       # чёрный квадрат
    draw.rectangle([150, 30, 230, 100], fill=0)       # ещё один чёрный квадрат
    draw.rectangle([30, 150, 230, 230], fill=0)       # большой прямоугольник
    draw.ellipse([90, 60, 170, 140], fill=0)           # круг
    # Горизонтальные полосы
    for y in range(110, 145, 10):
        draw.rectangle([30, y, 230, y + 5], fill=0)

    return img


def pad_data(data, block_size=16):
    """Дополняем данные до кратности размеру блока (PKCS7)"""
    padding_len = block_size - (len(data) % block_size)
    return data + bytes([padding_len] * padding_len)


def encrypt_ecb(data, key):
    """Шифрование в режиме ECB — каждый блок шифруется независимо"""
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad_data(data)
    return cipher.encrypt(padded)


def encrypt_cbc(data, key, iv):
    """Шифрование в режиме CBC — блоки связаны через XOR с предыдущим шифртекстом"""
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad_data(data)
    return cipher.encrypt(padded)


def encrypted_bytes_to_image(enc_data, width, height):
    """Преобразуем зашифрованные байты обратно в изображение для визуализации"""
    # Обрезаем или дополняем до нужного размера
    needed = width * height
    if len(enc_data) >= needed:
        pixels = enc_data[:needed]
    else:
        pixels = enc_data + b'\x00' * (needed - len(enc_data))
    img = Image.new('L', (width, height))
    img.putdata(list(pixels))
    return img


# === Графический интерфейс ===

class ECBDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Уязвимость режима ECB")
        self.root.resizable(False, False)

        # Размеры изображения
        self.img_width = 256
        self.img_height = 256

        # Ключ AES-128 (16 байт) и вектор инициализации для CBC
        self.key = os.urandom(16)
        self.iv = os.urandom(16)

        self.setup_ui()
        self.run_demo()

    def setup_ui(self):
        """Создаём элементы интерфейса"""
        # Заголовок
        title = ttk.Label(self.root, text="Демонстрация уязвимости режима ECB",
                          font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Описание
        desc_text = (
            "Одинаковые блоки открытого текста в ECB дают одинаковые блоки шифртекста.\n"
            "Поэтому визуальная структура изображения сохраняется после шифрования в ECB.\n"
            "В режиме CBC такой проблемы нет — каждый блок зависит от предыдущего."
        )
        desc = ttk.Label(self.root, text=desc_text, justify=tk.CENTER, wraplength=800)
        desc.pack(pady=5)

        # Фрейм с изображениями
        images_frame = ttk.Frame(self.root)
        images_frame.pack(padx=20, pady=10)

        # Три колонки: оригинал, ECB, CBC
        labels = ["Исходное изображение", "Зашифровано (ECB)", "Зашифровано (CBC)"]
        self.image_labels = []
        self.caption_labels = []

        for i, text in enumerate(labels):
            col_frame = ttk.Frame(images_frame)
            col_frame.grid(row=0, column=i, padx=15)

            caption = ttk.Label(col_frame, text=text, font=("Arial", 11, "bold"))
            caption.pack(pady=(0, 5))
            self.caption_labels.append(caption)

            img_label = ttk.Label(col_frame)
            img_label.pack()
            self.image_labels.append(img_label)

        # Кнопка перегенерации
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_regenerate = ttk.Button(btn_frame, text="Новый ключ и повтор",
                                         command=self.regenerate)
        self.btn_regenerate.pack(side=tk.LEFT, padx=5)

        # Информация о ключе
        self.key_label = ttk.Label(self.root, text="", font=("Consolas", 9))
        self.key_label.pack(pady=(0, 5))

        # Пояснение внизу
        explanation = ttk.Label(
            self.root,
            text=(
                "Вывод: в режиме ECB контуры фигур видны даже после шифрования,\n"
                "т.к. одинаковые участки изображения дают одинаковый шифртекст.\n"
                "Режим CBC устраняет эту проблему за счёт цепочки блоков."
            ),
            justify=tk.CENTER, foreground="dark red",
            font=("Arial", 10)
        )
        explanation.pack(pady=(5, 15))

    def run_demo(self):
        """Выполняем шифрование и отображаем результат"""
        # Создаём тестовое изображение
        original = create_test_image(self.img_width, self.img_height)
        raw_data = original.tobytes()  # пиксели как байты

        # Шифруем в ECB и CBC
        ecb_encrypted = encrypt_ecb(raw_data, self.key)
        cbc_encrypted = encrypt_cbc(raw_data, self.key, self.iv)

        # Преобразуем зашифрованные данные в изображения
        ecb_img = encrypted_bytes_to_image(ecb_encrypted, self.img_width, self.img_height)
        cbc_img = encrypted_bytes_to_image(cbc_encrypted, self.img_width, self.img_height)

        # Сохраняем ссылки на PhotoImage (чтобы сборщик мусора не удалил)
        self.tk_images = [
            ImageTk.PhotoImage(original),
            ImageTk.PhotoImage(ecb_img),
            ImageTk.PhotoImage(cbc_img),
        ]

        # Отображаем
        for i, tk_img in enumerate(self.tk_images):
            self.image_labels[i].configure(image=tk_img)

        # Показываем ключ
        self.key_label.configure(
            text=f"Ключ AES-128: {self.key.hex().upper()}   |   IV (для CBC): {self.iv.hex().upper()}"
        )

    def regenerate(self):
        """Генерируем новый ключ и повторяем шифрование"""
        self.key = os.urandom(16)
        self.iv = os.urandom(16)
        self.run_demo()


# === Запуск ===

if __name__ == "__main__":
    root = tk.Tk()
    app = ECBDemoApp(root)
    root.mainloop()
