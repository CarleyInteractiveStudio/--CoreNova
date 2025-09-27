#include "timer.h"
#include "idt.h"
#include <stdint.h>

extern void irq0_handler();

#define PIT_BASE_FREQUENCY 1193180

volatile uint64_t ticks = 0;

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

void timer_handler_64() {
    ticks++;
    outb(0x20, 0x20); // EOI
}

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
    outb(0x40, (uint8_t)(divisor & 0xFF));
    outb(0x40, (uint8_t)((divisor >> 8) & 0xFF));

    // Registrar el manejador en la IDT
    idt_set_gate(32, (uint64_t)irq0_handler, 0x08, 0x8E);
}