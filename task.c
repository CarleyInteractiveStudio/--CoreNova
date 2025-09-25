#include "task.h"
#include "kheap.h"
#include <stddef.h> // Para NULL

// La tarea que se está ejecutando actualmente.
volatile task_t *current_task;

// La cola de tareas listas para ejecutarse.
volatile task_t *task_queue;

// Próximo ID de proceso a asignar.
uint32_t next_pid = 1;

void tasking_init() {
    // Deshabilitar interrupciones mientras inicializamos.
    asm volatile("cli");

    // Crear la primera tarea (el kernel).
    current_task = (task_t*)kmalloc(sizeof(task_t));
    current_task->id = next_pid++;
    current_task->esp = 0; // El esp del kernel se manejará de forma especial.
    current_task->next = current_task; // La cola circular solo tiene un elemento.

    task_queue = current_task;

    // Habilitar interrupciones.
    asm volatile("sti");
}

void create_task(void (*entry_point)(void)) {
    task_t* new_task = (task_t*)kmalloc(sizeof(task_t));
    new_task->id = next_pid++;

    // Asignar una pila para la nueva tarea.
    uint32_t stack = (uint32_t)kmalloc(4096); // Pila de 4KB.
    new_task->esp = stack + 4096; // La pila crece hacia abajo.

    // Preparar la pila para el primer cambio de contexto.
    // Esto es un poco de magia para que `iret` funcione.
    new_task->esp -= sizeof(regs_t);
    regs_t* regs = (regs_t*)new_task->esp;
    regs->eip = (uint32_t)entry_point;
    regs->cs = 0x08; // Segmento de código del kernel.
    regs->eflags = 0x202; // Habilita interrupciones.

    // Añadir la nueva tarea a la cola circular.
    new_task->next = task_queue->next;
    task_queue->next = new_task;
}

uint32_t schedule(uint32_t current_esp) {
    if (!current_task) {
        return current_esp;
    }

    // Guardar el puntero de la pila de la tarea actual.
    current_task->esp = current_esp;

    // Avanzar a la siguiente tarea en la cola circular.
    current_task = current_task->next;

    // Devolver el puntero de la pila de la nueva tarea.
    return current_task->esp;
}