format PE Console

entry start

include 'win32a.inc'

;=================================================
section '.data' data readable writeable
;=================================================

        prompt db 'Enter x and a',10,0
        input db '%lf',0
        input_int db '%d',0
        output_int db '%d',10,0
        output_y1 db 'y1 = %5.3f',10,0
        output_y2 db 'y2 = %5.3f',10,0
        output_y db 'y  = %5.3f',10,0
        output db '%5.3f',10,0
        newline db '',10,0
        a dq 0
        x dq 0
        y1 dq 0
        y2 dq 0
        y dq 0
        i dd 0
        n dd 10
        temp dd 0
        reminder dq 0


;=================================================
section '.code' code readable writeable executable
;=================================================

start:
        invoke printf, prompt
        invoke scanf, input, x
        invoke scanf, input, a

        while_loop:
                finit
                fld qword [ds:x]
                mov [ds:temp], 2
                fild dword [ds:temp]
                fcomip st1
                jbe else_1
                if_1:
                ;---- y1 = 2 - x -----
                      fld qword [ds:x]
                      mov [ds:temp], 2
                      fild dword [ds:temp]
                      fsub qword [ds:x]
                      fstp [ds:y1] ; uptload to ram from fpu
                      ;---------------------
                      jmp if_1_out
                else_1:
                ;--- y1 = a + 3 ----
                     fld qword [ds:a]
                     mov [ds:temp], 3
                     fild dword [ds:temp]
                     fadd qword [ds:a]
                     fstp [ds:y1]
                     if_1_out:



                finit
                fld qword [ds:x]
                fld qword [ds:a] ; put 2 value to stack
                fcomip st1 ; if x>=2 go to else
                jbe else_2
                if_2:
                ;--- y2 = a - 1 ---
                     fld qword [ds:a]
                     mov [ds:temp], 1
                     fild dword [ds:temp]
                     fsubp
                     fstp [ds:y2]
                     ;--------------------
                     jmp if_2_out
                else_2:
                ;--- y2 = a*x - 1 ---
                     fld qword [ds:a]
                     fmul qword [ds:x]
                     mov [ds:temp], 1
                     fild dword [ds:temp]
                     fsubp
                     fstp [ds:y2]
                     ;----------------
                     if_2_out:


                ;--- y = y1 + y2 -----
                fld qword [ds:y1]
                fadd qword [ds:y2]
                fstp [ds:y]
                ;---------------------

                invoke printf, output_y1, dword [ds:y1], dword [ds:y1+4]
                invoke printf, output_y2, dword [ds:y2], dword [ds:y2+4]
                invoke printf, output_y, dword [ds:y], dword [ds:y+4]
                invoke printf, newline


                ;----- x++ -----------
                fld1 ; put 1 to fpu stack
                fadd qword [ds:x] ; add x to current fpu stack value
                fstp [ds:x] ; upload new value from fpu stack
                ;---------------------


                ;---- i++; i < n -----
                mov ecx, [ds:i]
                inc ecx
                cmp ecx, [ds:n]
                mov [ds:i], ecx
                jne while_loop
                ;---------------------
  
  invoke getch
  
  invoke ExitProcess, 0
;=================================================
section '.idata' data import readable
;=================================================
    library kernel32, 'kernel32.dll', msvcrt, 'msvcrt.dll'
    
    import  kernel32, ExitProcess, 'ExitProcess'
    import  msvcrt, printf, 'printf', getch, '_getch', scanf, 'scanf'