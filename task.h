#ifndef TASK_H
#define TASK_H

#include <stdint.h>

// --- Estado de la Tarea ---
typedef enum {
    TASK_READY,     // La tarea está lista para ejecutarse.
    TASK_RUNNING,   // La tarea se está ejecutando actualmente.
    TASK_FINISHED,  // La tarea ha completado su ejecución.
} task_state_t;

// --- Estructura Principal de la Tarea ---
typedef struct task {
    uint64_t id;
    task_state_t state;
    void *stack_pointer;    // Puntero al tope de la pila del kernel cuando la tarea no está activa.
    void *stack_base;       // Puntero a la base de la pila de la tarea (para liberarla con kfree).
    void (*entry_point)();  // Puntero a la función que la tarea debe ejecutar.
    struct task *next;      // Puntero a la siguiente tarea en la lista circular.
} task_t;

// --- Interfaz Pública de Gestión de Tareas ---

// Inicializa el sistema de multitarea.
void task_init();

// Crea una nueva tarea que comenzará a ejecutar la función en `entry_point`.
// Devuelve el ID de la nueva tarea o -1 si falla.
int task_create(void (*entry_point)());

// La función del planificador. Cambia a la siguiente tarea lista.
void schedule();

// Termina la tarea actual.
void task_exit();

#endif // TASK_H