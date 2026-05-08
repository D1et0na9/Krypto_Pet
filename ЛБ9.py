import tkinter as tk
from tkinter import ttk, scrolledtext
import random


def rc4_keystream(key, n):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    out = []
    i = j = 0
    for _ in range(n):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) % 256])
    return out


def run_experiment(num_keys, stream_len, key_len, log):
    counts = [[0] * 256 for _ in range(stream_len)]
    for _ in range(num_keys):
        key = bytes(random.randint(0, 255) for _ in range(key_len))
        ks = rc4_keystream(key, stream_len)
        for pos, b in enumerate(ks):
            counts[pos][b] += 1

    expected = num_keys / 256.0
    log.insert(tk.END, f"=== Эксперимент RC4: {num_keys} ключей, длина {key_len} байт ===\n")
    log.insert(tk.END, f"Ожидаемая частота для каждого байта: {expected:.2f}\n\n")
    log.insert(tk.END, "Поз | Частота 0 | Отклонение от ожид. | Самый частый байт\n")
    log.insert(tk.END, "-" * 60 + "\n")

    for pos in range(stream_len):
        zero = counts[pos][0]
        dev = (zero - expected) / expected * 100
        top_byte = max(range(256), key=lambda b: counts[pos][b])
        top_cnt = counts[pos][top_byte]
        log.insert(tk.END,
                   f"{pos:3d} | {zero:5d}     | {dev:+6.2f}%             | "
                   f"0x{top_byte:02X} ({top_cnt})\n")

    log.insert(tk.END, "\n--- Вывод ---\n")
    log.insert(tk.END,
               "Второй байт keystream (позиция 1) с вероятностью ~2/256\n"
               "равен 0 (вместо 1/256). Это известная уязвимость Mantin-Shamir.\n"
               "В WEP IV передаётся открыто и склеивается с ключом, поэтому\n"
               "слабые первые байты keystream напрямую раскрывают информацию\n"
               "о секретном ключе — атаки FMS, KoreK, PTW ломают WEP за минуты.\n"
               "Защита: отбрасывать первые 256-3072 байт keystream (RC4-drop).\n\n")
    log.see(tk.END)


def on_run():
    log.delete("1.0", tk.END)
    try:
        n = int(num_var.get())
        L = int(len_var.get())
        k = int(key_var.get())
    except ValueError:
        log.insert(tk.END, "Введите числа\n")
        return
    run_experiment(n, L, k, log)


root = tk.Tk()
root.title("ЛБ9 Вариант 4: уязвимость RC4")
root.geometry("780x600")

frm = ttk.Frame(root, padding=10)
frm.pack(fill=tk.X)

num_var = tk.StringVar(value="1000")
len_var = tk.StringVar(value="16")
key_var = tk.StringVar(value="16")

ttk.Label(frm, text="Кол-во ключей:").grid(row=0, column=0, sticky="w")
ttk.Entry(frm, textvariable=num_var, width=10).grid(row=0, column=1, padx=5)
ttk.Label(frm, text="Длина keystream:").grid(row=0, column=2, sticky="w")
ttk.Entry(frm, textvariable=len_var, width=10).grid(row=0, column=3, padx=5)
ttk.Label(frm, text="Длина ключа (байт):").grid(row=0, column=4, sticky="w")
ttk.Entry(frm, textvariable=key_var, width=10).grid(row=0, column=5, padx=5)
ttk.Button(frm, text="Запустить", command=on_run).grid(row=0, column=6, padx=10)

log = scrolledtext.ScrolledText(root, font=("Consolas", 10))
log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
