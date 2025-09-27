#include "keyboard.h"
#include "idt.h"
#include <stdint.h>

// --- Constantes y Variables Globales del Módulo ---
#define LINE_BUFFER_SIZE 256

static char line_buffer[LINE_BUFFER_SIZE];
static int buffer_pos = 0;
static line_handler_t line_handler = 0; // Puntero a la función que procesará la línea

// --- Declaraciones de funciones ---
extern void kprint(const char *str);
extern void irq1_handler();

// --- Funciones de I/O ---
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

// Mapa de scancodes a caracteres ASCII (solo para teclado US)
const char scancode_to_char[] = {
  0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
  '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
  0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
  '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
};

// --- Implementación de la Interfaz Pública ---
void keyboard_init() {
    idt_set_gate(33, (uint64_t)irq1_handler, 0x08, 0x8E);
}

void keyboard_set_line_handler(line_handler_t handler) {
    line_handler = handler;
}

// --- Manejador de Interrupción del Teclado ---
void keyboard_handler_64() {
    uint8_t scancode = inb(0x60);

    if (scancode < sizeof(scancode_to_char)) {
        char c = scancode_to_char[scancode];

        if (c == '\b') { // Manejo de retroceso
            if (buffer_pos > 0) {
                buffer_pos--;
                kprint("\b"); // Mueve el cursor hacia atrás en la pantalla
            }
        } else if (c == '\n') { // Manejo de Enter
            kprint("\n");
            line_buffer[buffer_pos] = '\0'; // Terminar la cadena
            if (line_handler) {
                line_handler(line_buffer);
            }
            buffer_pos = 0; // Resetear el búfer
        } else if (c != 0) { // Manejo de otros caracteres
            if (buffer_pos < LINE_BUFFER_SIZE - 1) {
                line_buffer[buffer_pos++] = c;
                char str[2] = {c, '\0'};
                kprint(str); // Mostrar el carácter en pantalla
            }
        }
    }

    outb(0x20, 0x20); // Enviar EOI al PIC maestro
}