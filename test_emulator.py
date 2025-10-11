import pytest
import emulator_6  # импортируем весь модуль

# фикстура для подготовки тестовой VFS
@pytest.fixture
def setup_vfs():
    root = emulator_6.Dir("/")
    file1 = emulator_6.File("file.txt", "hello world")
    file2 = emulator_6.File("duplicates.txt", "a\na\nb\nb\nc\n")
    binf = emulator_6.File("binfile.bin", b"Hello", is_binary=True)
    docs = emulator_6.Dir("docs", root)
    root.children["file.txt"] = file1
    root.children["duplicates.txt"] = file2
    root.children["binfile.bin"] = binf
    root.children["docs"] = docs
    return root

# Проверка: ls выводит список файлов и возвращает статус "ok"
def test_ls(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("ls", [])
    assert "file.txt" in out
    assert status == "ok"

# Проверка: cat корректно выводит содержимое текстового файла
def test_cat_text(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("cat", ["file.txt"])
    assert "hello world" in out
    assert status == "ok"

# Проверка: cat корректно обрабатывает бинарный файл
def test_cat_binary(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("cat", ["binfile.bin"])
    assert "binary data" in out
    assert status == "ok"

# Проверка: uniq удаляет подряд идущие дубликаты строк
def test_uniq_basic(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("uniq", ["duplicates.txt"])
    assert "a" in out and "b" in out
    assert status == "ok"

# Проверка: chmod выдаёт ошибку при неверном режиме
def test_chmod_invalid_mode(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("chmod", ["abc", "file.txt"])
    assert "invalid mode" in out
    assert status == "error"

# Проверка: chmod успешно меняет права файла
def test_chmod_success(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("chmod", ["600", "file.txt"])
    assert status == "ok"
    assert emulator_6.VFS_ROOT.children["file.txt"].mode == 0o600

# Проверка: echo корректно выводит переданные аргументы
def test_echo(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("echo", ["Hello", "World"])
    assert out == "Hello World"
    assert status == "ok"

# Проверка: cd успешно переходит в существующую директорию
def test_cd_into_dir(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("cd", ["docs"])
    assert "текущая директория" in out
    assert emulator_6.CWD.name == "docs"
    assert status == "ok"

# Проверка: cd выдаёт ошибку при переходе в несуществующую директорию
def test_cd_nonexistent(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("cd", ["nosuchdir"])
    assert "No such file or directory" in out
    assert status == "error"

# Проверка: cd выдаёт ошибку при попытке перейти в файл
def test_cd_into_file(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("cd", ["file.txt"])
    assert "Not a directory" in out
    assert status == "error"

# Проверка: uniq -c считает количество повторов подряд идущих строк
def test_uniq_count(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("uniq", ["-c", "duplicates.txt"])
    assert "2 a" in out
    assert "2 b" in out
    assert status == "ok"

# Проверка: chmod успешно меняет права директории
def test_chmod_dir(setup_vfs):
    emulator_6.VFS_ROOT = setup_vfs
    emulator_6.CWD = setup_vfs
    out, status = emulator_6.execute("chmod", ["700", "docs"])
    assert status == "ok"
    assert emulator_6.VFS_ROOT.children["docs"].mode == 0o700
