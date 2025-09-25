; boot.s
; Define el encabezado Multiboot para que el cargador de arranque (GRUB/QEMU) nos reconozca.
section .multiboot
align 4
    dd 0x1BADB002        ; Número mágico.
    dd 0x00              ; Banderas (flags).
    dd - (0x1BADB002 + 0x00) ; Suma de comprobación.

; Pila de arranque temporal.
section .bootstrap_stack, nobits
align 4
stack_bottom:
resb 16384 ; 16 KB de pila.
stack_top:

; El punto de entrada que el cargador de arranque ejecutará.
section .text
global _start
extern kmain ; Llama a la función principal de nuestro kernel en C.

_start:
    ; Cambiar al modo de 32 bits y preparar el entorno.
    mov esp, stack_top   ; Configura el puntero de la pila.
    call kmain           ; Llama a nuestro kernel.

    ; Si el kernel alguna vez retorna (no debería), nos detenemos aquí.
    cli
.hang:
    hlt
    jmp .hang