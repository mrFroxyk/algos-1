nasm -f win32 pr2.asm -o pr2.obj
golink /entry:Start /console kernel32.dll user32.dll msvcrt.dll pr2.obj
./pr2.exe