#ifndef TASK_H
#define TASK_H

#include <stdint.h>

// Estructura para guardar el estado de los registros de la CPU
typedef struct regs
{
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax; // Registros guardados por pusha
    uint32_t eip, cs, eflags;                       // Guardados manualmente por la CPU en una interrupción
} regs_t;

// Enumeración de los estados de una tarea
typedef enum {
    TASK_READY,
    TASK_RUNNING,
    TASK_WAITING,
    TASK_ZOMBIE,
} task_state_t;

// Estructura del Bloque de Control de Tareas (TCB)
typedef struct task
{
    int id;                 // ID de la tarea
    task_state_t state;     // Estado actual de la tarea
    uint32_t esp;           // Puntero a la pila de la tarea
    struct task* next;      // Siguiente tarea en la lista
    int exit_code;          // Código de salida cuando la tarea es ZOMBIE
    struct task* parent;    // Tarea padre
} task_t;


// Inicializa el sistema de tareas
void tasking_init();

// Crea una nueva tarea
void create_task(void (*entry_point)(void), int is_user);

// Cambia a la siguiente tarea y devuelve el nuevo puntero de la pila.
uint32_t schedule(uint32_t current_esp);

#endif // TASK_H