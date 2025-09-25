#ifndef GDT_H
#define GDT_H

#include <stdint.h>

// Estructura de una entrada en la GDT
typedef struct {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_middle;
    uint8_t  access;
    uint8_t  granularity;
    uint8_t  base_high;
} __attribute__((packed)) gdt_entry_t;

// Puntero a la GDT
typedef struct {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed)) gdt_ptr_t;

// Estructura de Estado de Tarea (TSS)
typedef struct {
    uint32_t prev_tss;
    uint32_t esp0, ss0; // Pila y segmento de datos del kernel (Ring 0)
    uint32_t esp1, ss1;
    uint32_t esp2, ss2;
    uint32_t cr3, eip, eflags;
    uint32_t eax, ecx, edx, ebx, esp, ebp, esi, edi;
    uint32_t es, cs, ss, ds, fs, gs;
    uint32_t ldt;
    uint16_t trap, iomap_base;
} __attribute__((packed)) tss_entry_t;

// Inicializa la GDT y el TSS
void gdt_init();

#endif // GDT_H