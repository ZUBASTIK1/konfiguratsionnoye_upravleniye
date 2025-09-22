import tkinter as tk
import getpass, socket, shlex

# Получение данных ОС
user = getpass.getuser()
host = socket.gethostname()
prompt = f"{user}@{host}$"

# Создание окна
win = tk.Tk()
win.title(f"Эмулятор — [{user}@{host}]")
win.geometry("700x400")

# Поле вывода (только для чтения)
term = tk.Text(win, bg="black", fg="white", insertbackground="white", state="disabled")
term.pack(expand=True, fill="both")

# Поле ввода команд
entry = tk.Entry(win, bg="gray15", fg="white", insertbackground="white")
entry.pack(fill="x", ipady=0)
entry.focus()

# Начальный вывод
term.configure(state="normal")
term.insert("end", f"Эмулятор запущен. Введите команды: ls, cd, exit\nСессия: {user}@{host}\n\n")
term.insert("end", f"{prompt}")
term.configure(state="disabled")

# Обработчик команды
def on_enter(event):
    cmdline = entry.get().strip()
    entry.delete(0, "end")

    if not cmdline:
        return

    try:
        args = shlex.split(cmdline)
    except Exception as e:
        term.configure(state="normal")
        term.insert("end", f"\nparse error: {e}\n{prompt}")
        term.configure(state="disabled")
        term.see("end")
        return

    cmd = args[0]
    rest = args[1:]

    term.configure(state="normal")
    term.insert("end", f"\n{prompt} {cmdline}")

    if cmd == "exit":
        win.destroy()
        return
    elif cmd == "ls":
        term.insert("end", f"\ncommand: ls\nargs: {rest}")
    elif cmd == "cd":
        term.insert("end", f"\ncommand: cd\nargs: {rest}\nnote: директория не меняется (заглушка)")
    else:
        term.insert("end", f"\n{cmd}: command not found")

    term.insert("end", f"\n{prompt}")
    term.configure(state="disabled")
    term.see("end")

# Привязка Enter к обработчику
entry.bind("<Return>", on_enter)

# Запуск приложения
win.mainloop()
