section .data
    num1 dd 10
    num2 dd 20
    result dd 0

section .text
    global _start

_start:
    ; move num1 into eax
    mov eax, num1

    ; add num2 to eax
    add eax, num2

    ; move the result into the result variable
    mov result, eax

    ; exit the program
    mov eax, 1
    xor ebx, ebx
    int 0x80