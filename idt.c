#include "idt.h"

// Declaración de la función externa de ensamblador para cargar la IDT
extern void idt_load(idt_ptr_t* idt_ptr);

// Nuestra IDT
idt_entry_t idt_entries[256];
idt_ptr_t   idt_pointer;

// Función para configurar una entrada de la IDT
void idt_set_gate(uint8_t num, uint64_t base, uint16_t selector, uint8_t flags) {
    idt_entries[num].offset_1 = (base & 0xFFFF);
    idt_entries[num].offset_2 = (base >> 16) & 0xFFFF;
    idt_entries[num].offset_3 = (base >> 32) & 0xFFFFFFFF;

    idt_entries[num].selector = selector;
    idt_entries[num].type_attributes = flags;
    idt_entries[num].ist = 0;
    idt_entries[num].zero = 0;
}

// Inicializa la IDT
void idt_init() {
    idt_pointer.limit = sizeof(idt_entry_t) * 256 - 1;
    idt_pointer.base  = (uint64_t)&idt_entries;

    // TODO: Limpiar la tabla y configurar manejadores por defecto.

    idt_load(&idt_pointer);
}