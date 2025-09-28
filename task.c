#include "task.h"
#include "heap.h"
#include <stddef.h>

// --- Variables Globales ---
static task_t *current_task = NULL;
static task_t *task_list_head = NULL;
static uint64_t next_task_id = 0;

// --- Declaraciones Externas ---
extern void context_switch(void **old_task_sp, void *new_task_sp);

// --- Funciones Internas ---

// Envoltorio para la ejecución de la tarea.
// Llama a la función de entrada de la tarea actual y luego a task_exit.
void task_wrapper() {
    // Las interrupciones deben estar habilitadas para que el timer funcione,
    // pero la función de cambio de contexto podría deshabilitarlas.
    // Las re-habilitamos aquí para la nueva tarea.
    asm volatile("sti");

    current_task->entry_point();
    task_exit();
}

// --- Implementación de la Interfaz Pública ---

void task_init() {
    task_t *kernel_task = (task_t*)kmalloc(sizeof(task_t));
    if (kernel_task == NULL) return;

    kernel_task->id = next_task_id++;
    kernel_task->state = TASK_RUNNING;
    kernel_task->stack_pointer = NULL;
    kernel_task->stack_base = NULL;
    kernel_task->entry_point = NULL;

    kernel_task->next = kernel_task;
    task_list_head = kernel_task;
    current_task = kernel_task;
}

#define STACK_SIZE 4096

int task_create(void (*entry_point)()) {
    task_t *new_task = (task_t*)kmalloc(sizeof(task_t));
    if (new_task == NULL) return -1;

    void *stack = kmalloc(STACK_SIZE);
    if (stack == NULL) {
        kfree(new_task);
        return -1;
    }

    new_task->id = next_task_id++;
    new_task->state = TASK_READY;
    new_task->stack_base = stack;
    new_task->entry_point = entry_point;

    // Preparar la pila inicial de la nueva tarea
    uint64_t *stack_top = (uint64_t*)((uint8_t*)stack + STACK_SIZE);

    // 1. La "dirección de retorno" para context_switch -> la función task_wrapper.
    *(--stack_top) = (uint64_t)task_wrapper;

    // 2. Valores iniciales para los registros que context_switch restaura (r15 a rbp).
    //    Los ponemos a 0, ya que la tarea empieza desde cero.
    *(--stack_top) = 0; // r15
    *(--stack_top) = 0; // r14
    *(--stack_top) = 0; // r13
    *(--stack_top) = 0; // r12
    *(--stack_top) = 0; // rbx
    *(--stack_top) = 0; // rbp

    new_task->stack_pointer = stack_top;

    // Añadir la tarea a la lista circular
    new_task->next = task_list_head->next;
    task_list_head->next = new_task;

    return new_task->id;
}

void schedule() {
    if (current_task == NULL) return;

    task_t *next_task = current_task->next;
    // Bucle para encontrar la siguiente tarea que no esté terminada.
    while (next_task->state == TASK_FINISHED) {
        if (next_task == current_task) return; // No hay otras tareas que ejecutar.
        next_task = next_task->next;
    }

    // Si la siguiente tarea lista es la misma que la actual, no hacemos nada.
    if (next_task == current_task) return;

    task_t *old_task = current_task;

    if (old_task->state == TASK_RUNNING) {
        old_task->state = TASK_READY;
    }

    next_task->state = TASK_RUNNING;
    current_task = next_task;

    context_switch(&old_task->stack_pointer, next_task->stack_pointer);
}

void task_exit() {
    current_task->state = TASK_FINISHED;
    // NOTA: No liberamos la pila aquí porque podríamos estar ejecutándonos en ella.
    // Un sistema más complejo tendría una tarea "reaper" para limpiar las tareas terminadas.
    schedule();
    // No se debería llegar nunca a este punto.
    for(;;);
}