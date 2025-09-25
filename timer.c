#include "timer.h"
#include "idt.h"
#include <stdint.h>

// Declaración de funciones externas que definiremos en otros lugares.
void idt_set_gate(uint8_t num, uint32_t base, uint16_t selector, uint8_t flags);
extern void timer_interrupt_handler(); // El puente en ensamblador

// Frecuencia base del PIT en Hz.
#define PIT_BASE_FREQUENCY 1193180

// Variable para contar los "ticks" o latidos del sistema.
volatile uint32_t ticks = 0;

// Función para escribir en los puertos de hardware.
static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

// Declaración de la función schedule de task.c
uint32_t schedule(uint32_t current_esp);

// Esta función es llamada en cada interrupción del temporizador.
void timer_handler(uint32_t esp) {
    ticks++;

    // Enviar "Fin de Interrupción" (EOI) al controlador de interrupciones.
    outb(0x20, 0x20);

    // Llamar al planificador para cambiar de tarea.
    schedule(esp);
}

// Inicializa el temporizador (PIT).
void timer_init(unsigned int frequency) {
    // Registra nuestro manejador en la entrada 32 (IRQ0) de la IDT.
    idt_set_gate(32, (uint32_t)timer_interrupt_handler, 0x08, 0x8E);

    // Calcular el divisor.
    uint32_t divisor = PIT_BASE_FREQUENCY / frequency;

    // Enviar el comando de configuración al PIT (Canal 0, modo 2, acceso lo/hi).
    outb(0x43, 0x36);

    // Enviar los bytes del divisor.
    uint8_t l = (uint8_t)(divisor & 0xFF);
    uint8_t h = (uint8_t)((divisor >> 8) & 0xFF);
    outb(0x40, l);
    outb(0x40, h);
}