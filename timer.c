#include "timer.h"
#include "idt.h"
#include <stdint.h>

// Declaraciones de funciones externas
extern void idt_set_gate(uint8_t num, uint64_t base, uint16_t selector, uint8_t flags);
extern void irq0_handler(); // Nuestro stub en ensamblador

// Frecuencia base del PIT
#define PIT_BASE_FREQUENCY 1193180

// Contador de Ticks
volatile uint64_t ticks = 0;

// Funciones para I/O
static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}
static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

// Manejador de la interrupción del temporizador
void timer_handler_64() {
    ticks++;
    // Enviar Fin de Interrupción (EOI) al PIC
    outb(0x20, 0x20);
}

// Inicializa el temporizador (PIT)
void timer_init(uint32_t frequency) {
    // Remapear el PIC
    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x0);
    outb(0xA1, 0x0);

    // Configurar el PIT
    uint32_t divisor = PIT_BASE_FREQUENCY / frequency;
    outb(0x43, 0x36);
    uint8_t l = (uint8_t)(divisor & 0xFF);
    uint8_t h = (uint8_t)((divisor >> 8) & 0xFF);
    outb(0x40, l);
    outb(0x40, h);

    // Registrar el manejador en la IDT (IRQ0 es el vector 32)
    idt_set_gate(32, (uint64_t)irq0_handler, 0x08, 0x8E);
}