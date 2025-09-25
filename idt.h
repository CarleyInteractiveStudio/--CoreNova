#ifndef IDT_H
#define IDT_H

#include <stdint.h>

// Estructura de una entrada en la IDT de 64 bits
typedef struct {
    uint16_t offset_1;        // Offset bits 0-15
    uint16_t selector;        // Selector de segmento de código
    uint8_t  ist;             // Interrupt Stack Table offset
    uint8_t  type_attributes; // Tipo y atributos
    uint16_t offset_2;        // Offset bits 16-31
    uint32_t offset_3;        // Offset bits 32-63
    uint32_t zero;            // Reservado
} __attribute__((packed)) idt_entry_t;

// Puntero a la IDT
typedef struct {
    uint16_t limit;
    uint64_t base;
} __attribute__((packed)) idt_ptr_t;

// Inicializa la IDT
void idt_init();

#endif // IDT_H