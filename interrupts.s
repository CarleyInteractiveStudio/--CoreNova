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

    mov eax, esp      ; Mover el puntero de la pila actual a EAX.
    push eax          ; Ponerlo en la pila como argumento para timer_handler.
    call timer_handler
    pop eax           ; Limpiar el argumento de la pila.

    mov esp, eax      ; Cargar el nuevo puntero de la pila devuelto por schedule.

    popa
    iret

; --- Cargar el Directorio de Páginas y Activar la Paginación ---
global load_page_directory_and_enable_paging
load_page_directory_and_enable_paging:
    mov eax, [esp+4]  ; Obtiene la dirección del directorio de páginas.
    mov cr3, eax      ; Carga la dirección en el registro CR3.

    mov eax, cr0      ; Obtiene el registro de control CR0.
    or eax, 0x80000000 ; Activa el bit de paginación (bit 31).
    mov cr0, eax      ; Escribe de nuevo en CR0 para activar la paginación.

    ret