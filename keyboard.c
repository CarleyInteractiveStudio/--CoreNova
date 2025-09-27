#include "keyboard.h"
#include "idt.h"
#include <stdint.h>

// Declaraciones de funciones externas
extern void kprint(const char *str);
extern void irq1_handler(); // Nuestro futuro stub en ensamblador

// Función para leer del puerto de I/O
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

// Mapa de scancodes a caracteres ASCII
const char scancode_to_char[] = {
  0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
  '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
  0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
  '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
};

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

// Manejador de la interrupción del teclado
void keyboard_handler_64() {
    uint8_t scancode = inb(0x60);

    if (scancode < sizeof(scancode_to_char)) {
        char c = scancode_to_char[scancode];
        if (c != 0) {
            char str[2] = {c, '\0'};
            kprint(str);
        }
    }

    // IRQ1 es del PIC maestro. Solo necesitamos enviar EOI al maestro.
    outb(0x20, 0x20);
}

// Inicializa el controlador del teclado
void keyboard_init() {
    // Registrar el manejador en la IDT (IRQ1 es el vector 33)
    idt_set_gate(33, (uint64_t)irq1_handler, 0x08, 0x8E);
}