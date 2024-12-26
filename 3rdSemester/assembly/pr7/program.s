.data
    .align 4 @ Выравнивание по 4 байта
input_str:   .asciz " Hello world! I use Arch BTW "    @ Входная строка для теста
    .align 4 @ Выравнивание по 4 байта
buffer:      .space 100    @ Буфер для изменения строки
    .align 4 @ Выравнивание по 4 байта
block:       .space 12    @ Блок для вывода (3 слова по 4 байта)
    .align 4 @ Выравнивание по 4 байта
crlf:        
	.byte 0x0d, 0x0a, 0    @ Символ новой строки (CR+LF для Windows)

    .text
    .global _start    @ Объявление глобальной метки _start

_start:
    LDR R0, =input_str    @ Загружаем адрес строки в R0
    LDR R1, =buffer    @ Загружаем адрес буфера в R1
    BL remove_first_word    @ Вызов функции для удаления первого слова
    BL to_lower_case    @ Вызов функции для преобразования строки в нижний регистр

    ldr r10, =block    @ Загружаем адрес блока в r10
    mov r0, #1    @ Файловый дескриптор (stdout)
    str r0, [r10], #4    @ Сохраняем дескриптор в блок и инкрементируем указатель
    ldr r0, =buffer    @ Загружаем адрес буфера в r0
    str r0, [r10], #4    @ Сохраняем адрес буфера в блок и инкрементируем указатель
    mov r0, #100     @ Указываем длину строки (100 символов)
    str r0, [r10]    @ Сохраняем длину строки в блок
    sub r10, r10, #8     @ Возвращаем указатель на начало блока
    mov r0, #0x05     @ Указываем системный вызов для записи
    mov r1, r10     @ Указатель на блок параметров
    swi 0x123456      @ Вызов Windows API для записи в stdout

    @ Вывод перевода строки
   @ bl output_crlf      @ Вызов функции для вывода новой строки

    @ Выход из программы
    mov r0, #0x18    @ Системный вызов для выхода из программы
    mov r1, #0      @ Код возврата из программы
    swi 0x123456      @ Вызов системного вызова для завершения программы
    
remove_first_word:
skip_leading_spaces:
    LDRB R2, [R0]        @ Считываем байт из строки
    CMP R2, #' '    @ Проверяем, является ли символ пробелом
    BEQ advance_leading  @ Если пробел, переходим к следующему символу
    B check_first_non_space  @ Если не пробел, проверяем начало первого слова

advance_leading:
    ADD R0, R0, #1    @ Переходим к следующему символу в строке
    B skip_leading_spaces@ Возвращаемся к проверке пробелов

check_first_non_space:
    LDRB R2, [R0], #1    @ Считываем байт и инкрементируем указатель

check_space:
    CMP R2, #' '    @ Проверяем, является ли символ пробелом
    BEQ start_copy    @ Если пробел, начинаем копировать строку

    LDRB R2, [R0], #1    @ Считываем следующий символ
    B check_space    @ Проверяем его на пробел

start_copy:
copy_loop:
    LDRB R2, [R0], #1    @ Считываем байт и инкрементируем указатель
    STRB R2, [R1], #1    @ Копируем байт в буфер
    CMP R2, #0    @ Проверяем на конец строки
    BEQ end_copy    @ Если конец строки, завершаем копирование

    CMP R2, #' '    @ Проверяем, является ли символ пробелом
    BNE copy_loop    @ Если не пробел, продолжаем копирование
    LDRB R3, [R0]    @ Читаем следующий символ без инкремента
    CMP R3, #0    @ Проверяем на конец строки
    BNE copy_loop    @ Если не конец строки, продолжаем копирование
      @ Если символ пробел, то заканчиваем копирование

end_copy:
    MOV R2, #0    @ Записываем символ завершения строки (нулевой байт)
    STRB R2, [R1]    @ Сохраняем нулевой байт в буфер
    BX LR @ Возвращаемся из функции

to_lower_case:
    LDR R1, =buffer    @ Загружаем адрес буфера в R1
lower_loop:
    LDRB R2, [R1]    @ Считываем байт из буфера
    CMP R2, #0    @ Проверяем на конец строки
    BEQ end_lower    @ Если конец строки, завершаем

    CMP R2, #'A'    @ Проверяем, если символ >= 'A'
    BLT next_char    @ Если меньше 'A', переходим к следующему символу
    CMP R2, #'Z'    @ Проверяем, если символ <= 'Z'
    BGT next_char    @ Если больше 'Z', переходим к следующему символу
    ADD R2, R2, #32    @ Преобразуем в нижний регистр
    STRB R2, [R1]    @ Сохраняем преобразованный символ обратно в буфер

next_char:
    ADD R1, R1, #1    @ Переходим к следующему символу
    B lower_loop    @ Продолжаем цикл

end_lower:
    BX LR    @ Возвращаемся из функции

output_crlf:
    STMFD sp!, {r0-r1,lr} @ Сохраняем регистры в стек
    ldr r10, =block    @ Загружаем адрес блока снова
    mov r0, #1    @ Устанавливаем файловый дескриптор (stdout)
    str r0, [r10], #4    @ Сохраняем дескриптор в блок с инкрементом
    ldr r0, =crlf    @ Загружаем адрес перевода строки
    str r0, [r10], #4    @ Сохраняем адрес перевода строки в блок
    mov r0, #2    @ Устанавливаем длину CR+LF
    str r0, [r10]    @ Сохраняем длину
    sub r10, r10, #8    @ Возвращаем указатель на начало блока
    mov r0, #0x05    @ Системный вызов Write
    mov r1, r10    @ Указатель на блок параметров
    swi 0x123456    @ Вызов Windows API для записи в stdout
    LDMFD sp!, {r0-r1,pc}    @ Восстанавливаем регистры и возвращаемся из функции
