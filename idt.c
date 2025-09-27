#include "idt.h"

extern void idt_load(idt_ptr_t* idt_ptr);

idt_entry_t idt_entries[256];
idt_ptr_t   idt_pointer;

void idt_set_gate(uint8_t num, uint64_t base, uint16_t selector, uint8_t flags) {
    idt_entries[num].offset_1 = (base & 0xFFFF);
    idt_entries[num].offset_2 = (base >> 16) & 0xFFFF;
    idt_entries[num].offset_3 = (base >> 32) & 0xFFFFFFFF;
    idt_entries[num].selector = selector;
    idt_entries[num].type_attributes = flags;
    idt_entries[num].ist = 0;
    idt_entries[num].zero = 0;
}

void idt_init() {
    idt_pointer.limit = sizeof(idt_entry_t) * 256 - 1;
    idt_pointer.base  = (uint64_t)&idt_entries;

    // Limpiar la IDT (buena práctica)
    for (int i = 0; i < 256; i++) {
        // En un sistema real, aquí se pondría un manejador por defecto.
    }

    idt_load(&idt_pointer);
}