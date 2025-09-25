; interrupts.s - Manejadores de bajo nivel para 64 bits

; --- Cargar la IDT ---
global idt_load
idt_load:
    lidt [rdi] ; El primer argumento en x86_64 se pasa por RDI
    ret

; --- Manejadores de Interrupción (Stubs) ---
extern timer_handler_64 ; La función C que será llamada

global irq0_handler
irq0_handler:
    ; Guardar todos los registros de 64 bits que la función C podría usar
    push rax
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15

    ; Llamar al manejador en C
    call timer_handler_64

    ; Restaurar todos los registros
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    pop rax

    ; Volver de la interrupción
    iretq