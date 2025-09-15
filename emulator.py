import tkinter as tk
import getpass, socket, shlex

user = getpass.getuser()
host = socket.gethostname()
prompt = f"{user}@{host}$"

win = tk.Tk()
win.title(f"Эмулятор — [{user}@{host}]")
win.geometry("700x400")

term = tk.Text(win, bg="black", fg="white", insertbackground="white")
term.pack(expand=True, fill="both")
term.insert("end", f"Эмулятор запущен. Введите команды: ls, cd, exit\nСессия: {user}@{host}\n\n")
term.insert("end", prompt)
term.focus()

def on_enter(event):
    index = term.index("insert linestart")
    line = term.get(index, index + " lineend").strip()

    if not line or line == prompt.strip():
        return

    cmdline = line[len(prompt):]
    try:
        args = shlex.split(cmdline)
    except Exception as e:
        term.insert("end", f"\nparse error: {e}\n{prompt}")
        term.mark_set("insert", "end")
        term.see("insert")
        return "break"

    if not args:
        term.insert("end", f"\n{prompt}")
        term.mark_set("insert", "end")
        term.see("insert")
        return "break"

    cmd = args[0]
    rest = args[1:]

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
    term.mark_set("insert", "end")
    term.see("insert")
    return "break"

def on_key(event):
    insert_index = term.index("insert")
    line_start = term.index("insert linestart")
    prompt_end = line_start + f"+{len(prompt)}c"

    # Блокируем действия, если курсор левее приглашения
    if term.compare(insert_index, "<", prompt_end):
        return "break"

    # Если курсор на приглашении — блокируем Backspace, разрешаем пробел и ввод
    if term.compare(insert_index, "==", prompt_end):
        if event.keysym == "BackSpace":
            return "break"
        return  # разрешаем ввод

    # Если курсор правее — всё ок
    return

term.bind("<Return>", on_enter)
term.bind("<Key>", on_key)

win.mainloop()
