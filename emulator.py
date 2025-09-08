import tkinter as tk
import getpass, socket, shlex

user = getpass.getuser()
host = socket.gethostname()
prompt = f"{user}@{host}$ "

win = tk.Tk()
win.title(f"Эмулятор — [{user}@{host}]")
win.geometry("700x400")

term = tk.Text(win, bg="black", fg="white", insertbackground="white")
term.pack(expand=True, fill="both")
term.insert("end", f"Эмулятор запущен. Введите команды: ls, cd, exit\nСессия: {user}@{host}\n\n")
term.insert("end", prompt)
term.focus()

def on_enter(event):
    # Получаем всю строку, где находится курсор
    index = term.index("insert linestart")
    line = term.get(index, index + " lineend").strip()

    if not line or line == prompt.strip():
        return

    cmdline = line[len(prompt):]  # Убираем приглашение
    try:
        args = shlex.split(cmdline)
    except Exception as e:
        term.insert("end", f"\nparse error: {e}\n{prompt}")
        return

    if not args:
        term.insert("end", f"\n{prompt}")
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "exit":
        win.destroy()
    elif cmd == "ls":
        term.insert("end", f"\ncommand: ls\nargs: {rest}")
    elif cmd == "cd":
        term.insert("end", f"\ncommand: cd\nargs: {rest}\nnote: директория не меняется (заглушка)")
    else:
        term.insert("end", f"\n{cmd}: command not found")

    term.insert("end", f"\n{prompt}")
    return "break"

term.bind("<Return>", on_enter)

win.mainloop()
