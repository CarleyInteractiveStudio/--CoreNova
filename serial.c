#include "serial.h"
#include <stdint.h>

// --- Definiciones de Puertos para COM1 ---
#define SERIAL_PORT_COM1 0x3F8

// --- Funciones de I/O ---
static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

// --- Implementación del Controlador Serie ---

void serial_init() {
    outb(SERIAL_PORT_COM1 + 1, 0x00); // Deshabilitar interrupciones
    outb(SERIAL_PORT_COM1 + 3, 0x80); // Habilitar DLAB (para establecer la velocidad)
    outb(SERIAL_PORT_COM1 + 0, 0x03); // Establecer divisor a 3 (38400 baud)
    outb(SERIAL_PORT_COM1 + 1, 0x00); //
    outb(SERIAL_PORT_COM1 + 3, 0x03); // 8 bits, sin paridad, un bit de parada
    outb(SERIAL_PORT_COM1 + 2, 0xC7); // Habilitar FIFO, limpiarlas
    outb(SERIAL_PORT_COM1 + 4, 0x0B); // IRQs habilitadas, RTS/DSR establecido
}

// Comprueba si el búfer de transmisión está vacío.
static int is_transmit_empty() {
   return inb(SERIAL_PORT_COM1 + 5) & 0x20;
}

void serial_write_char(char c) {
    // Esperar a que el puerto esté listo para enviar.
    while (is_transmit_empty() == 0);

    // Si es un salto de línea, enviar un retorno de carro primero.
    if (c == '\n') {
        outb(SERIAL_PORT_COM1, '\r');
        // Esperar de nuevo.
        while (is_transmit_empty() == 0);
    }

    outb(SERIAL_PORT_COM1, c);
}