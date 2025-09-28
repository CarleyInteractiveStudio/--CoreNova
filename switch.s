section .text
global context_switch

; void context_switch(void **old_task_sp, void *new_task_sp);
; Argumentos:
; rdi: Puntero a la variable que almacena el puntero de la pila de la tarea antigua.
; rsi: El valor del puntero de la pila de la nueva tarea.

context_switch:
    ; 1. Guardar los registros que deben ser preservados por la función (callee-saved).
    ;    El orden de guardado debe ser el inverso al de restauración.
    push rbp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; 2. Guardar el puntero de la pila (rsp) de la tarea actual.
    ;    rdi contiene la dirección de old_task->stack_pointer.
    mov [rdi], rsp

    ; 3. Cambiar al puntero de la pila (rsp) de la nueva tarea.
    ;    rsi contiene el valor de new_task->stack_pointer.
    mov rsp, rsi

    ; 4. Restaurar los registros callee-saved desde la pila de la nueva tarea.
    ;    Esto carga el contexto de la nueva tarea.
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp

    ; 5. Retornar. La instrucción `ret` tomará la dirección de retorno
    ;    de la pila de la nueva tarea, completando el cambio.
    ret