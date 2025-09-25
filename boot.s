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

section .data
align 4
mboot_ptr: dd 0

; El punto de entrada que el cargador de arranque ejecutará.
section .text
global _start
extern kmain ; Llama a la función principal de nuestro kernel en C.

_start:
    ; Guardar el puntero a la estructura Multiboot
    mov dword [mboot_ptr], ebx

    ; Cambiar al modo de 32 bits y preparar el entorno.
    mov esp, stack_top   ; Configura el puntero de la pila.

    ; Buscar la dirección del initrd
    mov eax, [ebx+16] ; Puntero a la cuenta de módulos
    cmp eax, 0
    je .no_initrd

    mov eax, [ebx+20] ; Puntero a la tabla de módulos
    mov eax, [eax]    ; Dirección de inicio del primer módulo
    push eax          ; Poner la dirección del initrd en la pila
    jmp .call_kernel

.no_initrd:
    push 0            ; Poner 0 si no hay initrd

.call_kernel:
    push dword [mboot_ptr]  ; Poner el puntero de multiboot en la pila
    call kmain              ; Llama a nuestro kernel.

    ; Si el kernel alguna vez retorna (no debería), nos detenemos aquí.
    cli
.hang:
    hlt
    jmp .hang