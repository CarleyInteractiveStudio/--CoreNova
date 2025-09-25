#include "keyboard.h"
#include "idt.h"
#include <stdint.h>

// Declaración de funciones externas que definiremos en otros lugares.
extern void kprint(const char *str, int line); // De kernel.c
void idt_set_gate(uint8_t num, uint32_t base, uint16_t selector, uint8_t flags); // De idt.c
extern void keyboard_interrupt_handler(); // El puente en ensamblador

// Funciones para leer y escribir en los puertos de hardware.
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

// Mapa de scancodes (Set 1) a caracteres ASCII para el teclado US.
const char scancode_to_char[] = {
  0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
  '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
  0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
  '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
};

#include "task.h" // Para task_t y estados
#include <stddef.h> // Para NULL

extern task_t* current_task;

#define BUFFER_SIZE 256
static char keyboard_buffer[BUFFER_SIZE];
static uint32_t buffer_index = 0;
static volatile int enter_pressed = 0;

task_t* waiting_for_read = NULL;

void keyboard_read(char* buffer) {
    // Poner la tarea actual a esperar.
    waiting_for_read = (task_t*)current_task;
    waiting_for_read->state = TASK_WAITING;

    // Ceder el control hasta que se presione Enter.
    while(!enter_pressed);

    // Copiar el buffer y resetear.
    for(uint32_t i = 0; i < buffer_index; i++) buffer[i] = keyboard_buffer[i];
    buffer[buffer_index] = '\0';
    buffer_index = 0;
    enter_pressed = 0;
    waiting_for_read = NULL;
}

// Esta función es llamada cada vez que se presiona una tecla.
void keyboard_handler() {
    uint8_t scancode = inb(0x60);

    if (scancode < sizeof(scancode_to_char)) {
        char c = scancode_to_char[scancode];
        if (c != 0) {
            if (c == '\n') {
                keyboard_buffer[buffer_index] = '\0';
                kprint("\n", -1);
                enter_pressed = 1;
                if (waiting_for_read) {
                    waiting_for_read->state = TASK_READY;
                }
            } else if (c == '\b') {
                if (buffer_index > 0) {
                    buffer_index--;
                    kprint("\b", -1);
                }
            } else if (buffer_index < BUFFER_SIZE - 1) {
                keyboard_buffer[buffer_index++] = c;
                char str[2] = {c, '\0'};
                kprint(str, -1);
            }
        }
    }

    // Enviar "Fin de Interrupción" (EOI).
    outb(0x20, 0x20);
}

// Inicializa el teclado.
void keyboard_init() {
    // Registra nuestro manejador en la entrada 33 (IRQ1) de la IDT.
    idt_set_gate(33, (uint32_t)keyboard_interrupt_handler, 0x08, 0x8E);
}