import tkinter as tk
import getpass, socket, shlex
import argparse, xml.etree.ElementTree as ET
import csv, datetime, base64
from pathlib import Path
from collections import Counter

# --- Получаем имя пользователя и хост ---
user = getpass.getuser()
host = socket.gethostname()
prompt = f"{user}@{host}$ "

# --- Чтение параметров из командной строки ---
parser = argparse.ArgumentParser()
parser.add_argument("--vfs")
parser.add_argument("--log")
parser.add_argument("--script")
parser.add_argument("--config")
cli = parser.parse_args()

# --- Чтение конфигурационного XML-файла ---
cfg = {}
if cli.config:
    try:
        tree = ET.parse(cli.config)
        root = tree.getroot()
        cfg = {
            "vfs": root.findtext("vfs"),
            "log": root.findtext("log"),
            "script": root.findtext("script")
        }
    except Exception as e:
        print(f"[config] Ошибка чтения XML: {e}")

# --- Приоритет: CLI > XML ---
VFS_PATH = cli.vfs or cfg.get("vfs")
LOG_PATH = cli.log or cfg.get("log")
SCRIPT_PATH = cli.script or cfg.get("script")

# --- Логирование команд в CSV ---
def log_event(cmd, args, status):
    if not LOG_PATH:
        return
    try:
        file_exists = Path(LOG_PATH).exists()
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow(["timestamp", "user", "command", "args", "status"])
            writer.writerow([
                datetime.datetime.now().isoformat(timespec="seconds"),
                user,
                cmd,
                " ".join(args),
                status
            ])
    except Exception as e:
        print(f"[log] Ошибка записи: {e}")

# --- Структуры данных VFS ---
class VFSNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

class Dir(VFSNode):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.children = {}

class File(VFSNode):
    def __init__(self, name, content, is_binary=False, parent=None):
        super().__init__(name, parent)
        self.content = content
        self.is_binary = is_binary

VFS_ROOT = None
CWD = None

# --- Монтирование VFS ---
def mount_vfs(path):
    global VFS_ROOT, CWD
    if not path:
        return False, "путь к VFS не задан"
    try:
        if not Path(path).exists():
            return False, f"файл {path} не найден"

        tree = ET.parse(path)
        root = tree.getroot()
        if root.tag != "vfs":
            return False, "корневой тег должен быть <vfs>"

        def attach(child, parent_dir):
            if child.tag == "dir":
                name = child.attrib.get("name")
                d = Dir(name, parent_dir)
                parent_dir.children[name] = d
                for sub in child:
                    attach(sub, d)
            elif child.tag == "file":
                name = child.attrib.get("name")
                enc = child.attrib.get("encoding", "none")
                raw = child.text or ""
                if enc == "base64":
                    data = base64.b64decode(raw)
                    f = File(name, data, is_binary=True, parent=parent_dir)
                else:
                    f = File(name, raw, is_binary=False, parent=parent_dir)
                parent_dir.children[name] = f

        VFS_ROOT = Dir("/")
        for child in root:
            attach(child, VFS_ROOT)
        CWD = VFS_ROOT
        return True, f"VFS загружен из {path}"
    except Exception as e:
        return False, f"Ошибка загрузки VFS: {e}"

# --- GUI ---
win = tk.Tk()
win.title(f"Эмулятор — [{user}@{host}]")
win.geometry("700x400")

term = tk.Text(win, bg="black", fg="white", insertbackground="white", state="disabled")
term.pack(expand=True, fill="both")

entry = tk.Entry(win, bg="gray15", fg="white", insertbackground="white")
entry.pack(fill="x", ipady=0)
entry.focus()

term.configure(state="normal")
term.insert("end", f"Эмулятор запущен. Команды (Этап 4): ls, cd, echo, cat, uniq, exit\nСессия: {user}@{host}\n\n")
term.insert("end",
    f"Параметры запуска:\n"
    f"VFS: {VFS_PATH}\n"
    f"Log: {LOG_PATH}\n"
    f"Script: {SCRIPT_PATH}\n"
    f"Config: {cli.config}\n\n"
)

if VFS_PATH:
    ok, msg = mount_vfs(VFS_PATH)
    term.insert("end", f"{msg}\n\n")
else:
    term.insert("end", "VFS путь не задан\n\n")

term.insert("end", prompt)
term.configure(state="disabled")

# --- Выполнение команд ---
# --- Выполнение команд ---
def execute(cmd, args):
    global CWD
    output = ""
    status = "ok"

    if cmd == "exit":
        log_event(cmd, args, "exit")
        win.destroy()
        return

    elif cmd == "ls":
        if args:
            name = args[0]
            if name in CWD.children:
                node = CWD.children[name]
                if isinstance(node, Dir):
                    output = "  ".join(sorted(node.children.keys()))
                else:
                    output = node.name
            else:
                output = f"ls: {name}: No such file or directory"
                status = "error"
        else:
            output = "  ".join(sorted(CWD.children.keys()))

    elif cmd == "cd":
        if not args or args[0] == "/":
            CWD = VFS_ROOT
            output = f"текущая директория: {CWD.name}"
        else:
            name = args[0]
            if name == "..":
                if CWD.parent:
                    CWD = CWD.parent
                output = f"текущая директория: {CWD.name}"
            elif name not in CWD.children:
                output = f"cd: {name}: No such file or directory"
                status = "error"
            else:
                node = CWD.children[name]
                if isinstance(node, Dir):
                    CWD = node
                    output = f"текущая директория: {CWD.name}"
                else:
                    output = f"cd: {name}: Not a directory"
                    status = "error"

    elif cmd == "echo":
        output = " ".join(args)

    elif cmd == "cat":
        if not args:
            output = "cat: missing operand"
            status = "error"
        else:
            name = args[0]
            if name in CWD.children:
                node = CWD.children[name]
                if isinstance(node, Dir):
                    output = f"cat: {name}: Is a directory"
                    status = "error"
                else:
                    if node.is_binary:
                        raw = node.content
                        # показываем размер и первые 200 байт в «читаемом» виде
                        preview = "".join(chr(b) if 32 <= b < 127 else "." for b in raw[:200])
                        output = f"[binary data: {len(raw)} bytes]\n{preview}"
                    else:
                        output = node.content
            else:
                output = f"cat: {name}: No such file"
                status = "error"


    elif cmd == "uniq":
        if not args:
            output = "uniq: missing operand"
            status = "error"
        else:
            flags = [a for a in args if a.startswith("-")]
            positional = [a for a in args if not a.startswith("-")]
            count_mode = "-c" in flags

            if len(positional) == 0:
                output = "uniq: missing operand"
                status = "error"
            else:
                name = positional[-1]
                if name not in CWD.children:
                    output = f"uniq: {name}: No such file"
                    status = "error"
                else:
                    node = CWD.children[name]
                    if isinstance(node, Dir):
                        output = f"uniq: {name}: Is a directory"
                        status = "error"
                    elif node.is_binary:
                        output = f"uniq: {name}: Binary file not supported"
                        status = "error"
                    else:
                        lines = node.content.splitlines()
                        if count_mode:
                            # считаем подряд идущие одинаковые строки
                            result = []
                            prev = None
                            count = 0
                            for line in lines:
                                if line == prev:
                                    count += 1
                                else:
                                    if prev is not None:
                                        result.append(f"{count} {prev}")
                                    prev = line
                                    count = 1
                            if prev is not None:
                                result.append(f"{count} {prev}")
                            output = "\n".join(result)
                        else:
                            result = []
                            prev = None
                            for line in lines:
                                if line != prev:
                                    result.append(line)
                                prev = line
                            output = "\n".join(result)

    else:
        output = f"{cmd}: command not found"
        status = "error"

    term.configure(state="normal")
    term.insert("end", f"\n{output}\n{prompt}")
    term.configure(state="disabled")
    term.see("end")

    log_event(cmd, args, status)


# --- Обработка ввода ---
def on_enter(event):
    cmdline = entry.get().strip()
    entry.delete(0, "end")
    if not cmdline:
        return
    try:
        parts = shlex.split(cmdline)
    except Exception as e:
        term.configure(state="normal")
        term.insert("end", f"\nparse error: {e}\n{prompt}")
        term.configure(state="disabled")
        term.see("end")
        return
    cmd, args = parts[0], parts[1:]
    term.configure(state="normal")
    term.insert("end", f"\n{prompt}{cmdline}")
    term.configure(state="disabled")
    execute(cmd, args)

entry.bind("<Return>", on_enter)


# --- Выполнение стартового скрипта ---
def run_script(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        term.configure(state="normal")
        term.insert("end", f"\n[script] Ошибка чтения: {e}\n{prompt}")
        term.configure(state="disabled")
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        term.configure(state="normal")
        term.insert("end", f"\n{prompt}{line}")
        term.configure(state="disabled")
        try:
            parts = shlex.split(line)
        except Exception as e:
            term.configure(state="normal")
            term.insert("end", f"\n[script] parse error: {e}\n{prompt}")
            term.configure(state="disabled")
            continue
        if not parts:
            continue
        cmd, args = parts[0], parts[1:]
        if cmd == "exit":
            log_event(cmd, args, "exit")
            win.after(0, win.destroy)
            return
        execute(cmd, args)

if SCRIPT_PATH:
    run_script(SCRIPT_PATH)

# --- Запуск GUI ---
win.mainloop()
