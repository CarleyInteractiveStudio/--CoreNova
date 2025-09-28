; interrupts.s - Manejadores de bajo nivel para 64 bits

; --- Funciones exportadas ---
global idt_load
global irq0_handler
global irq1_handler

; --- Funciones importadas ---
extern timer_and_schedule   ; La nueva función que llamará el temporizador
extern keyboard_handler_64

section .text

; --- Cargar la IDT ---
idt_load:
    lidt [rdi]
    ret

; --- Stub para IRQ0 (Temporizador) ---
; Esta interrupción guardará el estado completo y llamará al planificador.
irq0_handler:
    ; Guardar todos los registros de propósito general. El orden es importante.
    push rax
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push rbp
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15

    ; El puntero de pila (rsp) ahora apunta a la estructura de registros guardados.
    ; Lo pasamos como primer argumento (en rdi) a nuestra función C.
    mov rdi, rsp

    ; Llamar al manejador C. Este devolverá el puntero a la pila de la tarea
    ; que debe ejecutarse a continuación.
    call timer_and_schedule

    ; El valor de retorno (el nuevo puntero de pila) está en rax. Lo movemos a rsp.
    mov rsp, rax

    ; Restaurar todos los registros desde la (posiblemente nueva) pila.
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rbp
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    pop rax

    ; iretq restaurará rip, cs, rflags, etc., que la CPU guardó automáticamente.
    iretq

; --- Stub para IRQ1 (Teclado) ---
; Este no necesita cambiar, ya que no activa el planificador.
irq1_handler:
    push rax; push rbx; push rcx; push rdx; push rsi; push rdi
    push r8; push r9; push r10; push r11; push r12; push r13; push r14; push r15
    call keyboard_handler_64
    pop r15; pop r14; pop r13; pop r12; pop r11; pop r10; pop r9; pop r8
    pop rdi; pop rsi; pop rdx; pop rcx; pop rbx; pop rax
    iretq