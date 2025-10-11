@echo off
echo === ����: ��������� VFS ===
python emulator_3.py --vfs vfs_min.xml --log test_min.csv --script test_min.txt

echo === ����: ��᪮�쪮 䠩��� � ����� ===
python emulator_3.py --vfs vfs_docs.xml --log test_docs.csv --script test_docs.txt

echo === ����: ����������� 3 �஢�� ===
python emulator_3.py --vfs vfs_nested.xml --log test_nested.csv --script test_nested.txt

echo === ����: ��ࠡ�⪠ �訡�� (���� VFS) ===
python emulator_3.py --vfs error_vfs.xml --log test_error.csv --script test_error.txt

echo === ��⮢� ===
pause
