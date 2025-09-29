@echo off
echo === Тест: минимальный VFS ===
python emulator_2.py --vfs vfs_min.xml --log test_min.csv --script test_min.txt

echo === Тест: несколько файлов и папок ===
python emulator_2.py --vfs vfs_docs.xml --log test_docs.csv --script test_docs.txt

echo === Тест: вложенность 3 уровня ===
python emulator_2.py --vfs vfs_nested.xml --log test_nested.csv --script test_nested.txt

echo === Тест: обработка ошибок (битый VFS) ===
python emulator_2.py --vfs error_vfs.xml --log test_error.csv --script test_error.txt

echo === Готово ===
pause
