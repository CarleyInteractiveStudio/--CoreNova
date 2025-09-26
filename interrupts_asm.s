; interrupts_asm.s - Funciones de bajo nivel para interrupciones y paginación (Versión Definitiva)

; --- Funciones exportadas ---
global idt_load
global load_pml4
global irq0_handler

; --- Funciones importadas ---
extern timer_handler_64

section .text

; --- Cargar la IDT ---
idt_load:
    lidt [rdi]
    ret

; --- Cargar el nuevo mapa de memoria (PML4) ---
load_pml4:
    mov cr3, rdi
    ret

; --- Stub para IRQ0 (Temporizador) ---
irq0_handler:
    ; Guardar todos los registros de 64 bits
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