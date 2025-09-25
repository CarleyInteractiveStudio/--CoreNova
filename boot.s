; boot.s - Cargador de arranque de 64 bits compatible con Multiboot2 (Versión Corregida)

; --- Cabecera Multiboot2 ---
section .multiboot_header
header_start:
    dd 0xE85250D6                ; Número mágico de Multiboot2
    dd 0                         ; Arquitectura (0 = 32-bit, compatible)
    dd header_end - header_start ; Longitud de la cabecera
    dd -(0xE85250D6 + 0 + (header_end - header_start)) ; Suma de comprobación

    ; Tag de fin de la cabecera (requerido)
    dw 0
    dw 0
    dd 8
header_end:

; --- Pila del Kernel ---
section .bss
align 16
stack_bottom:
    resb 16384 ; 16KB de pila
stack_top:

; --- Código de Arranque ---
section .text
global _start
extern kmain

_start:
    ; Configurar el puntero de la pila
    mov rsp, stack_top

    ; Limpiar registros de segmento
    xor ax, ax
    mov ss, ax
    mov ds, ax
    mov es, ax

    ; Pasar info de Multiboot y llamar al kernel
    call kmain

    ; Detener si el kernel retorna
    cli
.hang:
    hlt
    jmp .hang