; interrupts.s - Manejadores de bajo nivel para 64 bits (Versión Corregida y Completa)

; --- Funciones exportadas ---
global idt_load
global irq0_handler
global irq1_handler

; --- Funciones importadas ---
extern timer_handler_64
extern keyboard_handler_64

section .text

; --- Cargar la IDT ---
idt_load:
    lidt [rdi]
    ret

; --- Stub para IRQ0 (Temporizador) ---
irq0_handler:
    push rax; push rbx; push rcx; push rdx; push rsi; push rdi
    push r8; push r9; push r10; push r11; push r12; push r13; push r14; push r15
    call timer_handler_64
    pop r15; pop r14; pop r13; pop r12; pop r11; pop r10; pop r9; pop r8
    pop rdi; pop rsi; pop rdx; pop rcx; pop rbx; pop rax
    iretq

; --- Stub para IRQ1 (Teclado) ---
irq1_handler:
    push rax; push rbx; push rcx; push rdx; push rsi; push rdi
    push r8; push r9; push r10; push r11; push r12; push r13; push r14; push r15
    call keyboard_handler_64
    pop r15; pop r14; pop r13; pop r12; pop r11; pop r10; pop r9; pop r8
    pop rdi; pop rsi; pop rdx; pop rcx; pop rbx; pop rax
    iretq