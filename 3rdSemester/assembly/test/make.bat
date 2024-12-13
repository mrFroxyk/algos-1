@echo off
REM Компиляция asm файла
nasm -f win32 "oche.asm" -o "oche.obj"

REM Линковка obj файла
golink /console kernel32.dll msvcrt.dll "oche.obj"

REM Запуск скомпилированного exe файла
"oche.exe"
