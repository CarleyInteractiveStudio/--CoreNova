; boot.s - Cargador de arranque de 64 bits compatible con Multiboot2

section .multiboot_header
header_start:
    dd 0xE85250D6                ; Número mágico de Multiboot2
    dd 0                         ; Arquitectura (0 = 32-bit, compatible)
    dd header_end - header_start ; Longitud de la cabecera
    dd -(0xE85250D6 + 0 + (header_end - header_start)) ; Suma de comprobación

    dw 0, 0, 8 ; Tag de fin
header_end:

section .bss
align 16
stack_bottom:
    resb 16384 ; 16KB de pila
stack_top:

section .text
global _start
extern kmain

_start:
    mov rsp, stack_top
    xor ax, ax
    mov ss, ax
    mov ds, ax
    mov es, ax
    call kmain
    cli
.hang:
    hlt
    jmp .hang