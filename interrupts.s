; interrupts.s - Manejadores de interrupciones de bajo nivel.

; --- Cargar la IDT ---
global idt_load
idt_load:
    mov eax, [esp+4]
    lidt [eax]
    ret

; --- Manejador de Interrupción del Teclado (IRQ1) ---
global keyboard_interrupt_handler
extern keyboard_handler

keyboard_interrupt_handler:
    ; Guardar todos los registros generales.
    pusha

    ; Llamar a nuestro manejador en C.
    call keyboard_handler

    ; Restaurar todos los registros generales.
    popa

    ; La instrucción iret (interrupt return) saca de la pila
    ; EIP, CS, EFLAGS, ESP y SS, restaurando el estado del programa interrumpido.
    iret

; --- Manejador de Interrupción del Temporizador (IRQ0) ---
global timer_interrupt_handler
extern timer_handler

timer_interrupt_handler:
    pusha
    call timer_handler
    popa
    iret