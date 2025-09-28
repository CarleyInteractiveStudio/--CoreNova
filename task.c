#include "task.h"
#include "heap.h"
#include "serial.h" // Para depuración
#include <stddef.h>

// --- Definiciones ---
#define STACK_SIZE 4096

// Estructura que coincide con los registros guardados por irq0_handler
typedef struct {
    uint64_t r15, r14, r13, r12, r11, r10, r9, r8;
    uint64_t rbp, rdi, rsi, rdx, rcx, rbx, rax;
} pushed_registers_t;

// Estructura que coincide con lo que la CPU guarda en una interrupción
typedef struct {
    uint64_t rip;
    uint64_t cs;
    uint64_t rflags;
    uint64_t rsp;
    uint64_t ss;
} interrupt_stack_frame_t;


// --- Variables Globales ---
static task_t *current_task = NULL;
static task_t *task_list_head = NULL;
static uint64_t next_task_id = 0;

// --- Funciones Internas ---
void task_wrapper();

// --- Implementación de la Interfaz Pública ---

void task_init() {
    task_t *kernel_task = (task_t*)kmalloc(sizeof(task_t));
    kernel_task->id = next_task_id++;
    kernel_task->state = TASK_RUNNING;
    kernel_task->stack_pointer = NULL;
    kernel_task->stack_base = NULL;
    kernel_task->entry_point = NULL;
    kernel_task->next = kernel_task;
    task_list_head = kernel_task;
    current_task = kernel_task;
}

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
    uint8_t *stack_top = (uint8_t*)stack + STACK_SIZE;

    // 1. Crear un marco de interrupción falso
    stack_top -= sizeof(interrupt_stack_frame_t);
    interrupt_stack_frame_t *frame = (interrupt_stack_frame_t*)stack_top;
    frame->rip = (uint64_t)task_wrapper;
    frame->cs = 0x08; // Segmento de código del kernel
    frame->rflags = 0x202; // Habilitar interrupciones
    frame->rsp = (uint64_t)stack_top;
    frame->ss = 0x10; // Segmento de datos del kernel

    // 2. Poner los valores iniciales de los registros guardados por irq0_handler
    stack_top -= sizeof(pushed_registers_t);
    pushed_registers_t *regs = (pushed_registers_t*)stack_top;
    for(int i=0; i<sizeof(pushed_registers_t)/8; i++) ((uint64_t*)regs)[i] = 0;

    new_task->stack_pointer = stack_top;

    // Añadir la tarea a la lista circular
    new_task->next = task_list_head->next;
    task_list_head->next = new_task;

    return new_task->id;
}

void* schedule(void *current_sp) {
    // 1. Guardar el puntero de la pila de la tarea que fue interrumpida.
    current_task->stack_pointer = current_sp;

    // 2. Encontrar la siguiente tarea que esté lista para ejecutarse.
    task_t *next_task = current_task;
    do {
        next_task = next_task->next;
        if (next_task->state == TASK_READY) {
            break; // Encontramos una.
        }
    } while (next_task != current_task);

    // 3. Si no encontramos otra tarea lista (o solo hay una), no hay cambio.
    if (next_task == current_task || next_task->state != TASK_READY) {
        return current_task->stack_pointer;
    }

    // 4. Realizar el cambio de tarea.
    task_t *old_task = current_task;

    // Marcar la tarea antigua como lista (si no es la del kernel que nunca se detiene).
    if (old_task->state == TASK_RUNNING) {
        old_task->state = TASK_READY;
    }

    // Marcar la nueva tarea como en ejecución.
    next_task->state = TASK_RUNNING;
    current_task = next_task;

    // 5. Devolver el puntero de la pila de la nueva tarea al manejador de interrupción.
    return current_task->stack_pointer;
}

void task_wrapper() {
    current_task->entry_point();
    task_exit();
}

void task_exit() {
    current_task->state = TASK_FINISHED;
    // Bucle infinito, el planificador ya no seleccionará esta tarea.
    for(;;) {
        asm volatile("hlt");
    }
}