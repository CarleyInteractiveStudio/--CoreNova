#ifndef IDT_H
#define IDT_H

#include <stdint.h>

// Estructura de una entrada en la IDT de 64 bits
typedef struct {
    uint16_t offset_1;
    uint16_t selector;
    uint8_t  ist;
    uint8_t  type_attributes;
    uint16_t offset_2;
    uint32_t offset_3;
    uint32_t zero;
} __attribute__((packed)) idt_entry_t;

// Puntero a la IDT
typedef struct {
    uint16_t limit;
    uint64_t base;
} __attribute__((packed)) idt_ptr_t;

// Funciones
void idt_init();
void idt_set_gate(uint8_t num, uint64_t base, uint16_t selector, uint8_t flags);

#endif // IDT_H