#include "idt.h"
#include <stddef.h> // Para NULL

// Declaramos nuestra tabla IDT con 256 entradas.
idt_entry_t idt_entries[256];
idt_ptr_t   idt_pointer;

// Función externa (definida en ensamblador) para cargar nuestra IDT.
extern void idt_load(idt_ptr_t* idt_pointer);

/*
 * Configura una entrada en la tabla IDT.
 * num: El número de la interrupción (0-255).
 * base: La dirección de la función que manejará la interrupción.
 * selector: El selector del segmento de código.
 * flags: Banderas de configuración para esta entrada.
 */
void idt_set_gate(uint8_t num, uint32_t base, uint16_t selector, uint8_t flags) {
    idt_entries[num].base_low = base & 0xFFFF;
    idt_entries[num].base_high = (base >> 16) & 0xFFFF;
    idt_entries[num].selector = selector;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}

/*
 * Inicializa la Tabla de Descriptores de Interrupciones.
 */
void idt_init() {
    // Configura el puntero de la IDT.
    idt_pointer.limit = sizeof(idt_entry_t) * 256 - 1;
    idt_pointer.base = (uint32_t)&idt_entries;

    // Limpia la tabla IDT (opcional, pero buena práctica).
    // Por ahora, no configuraremos ninguna interrupción aquí.
    // Lo haremos cuando inicialicemos el teclado.
    for (int i = 0; i < 256; i++) {
        // En un sistema real, aquí se pondría un manejador por defecto.
    }

    // Carga la IDT en la CPU.
    idt_load(&idt_pointer);
}