#include "gdt.h"

// Declaración de funciones externas de ensamblador
extern void gdt_flush(uint32_t gdt_ptr);
extern void tss_flush();

// La GDT y su puntero
gdt_entry_t gdt_entries[6];
gdt_ptr_t   gdt_pointer;

// La Estructura de Estado de Tarea (TSS)
tss_entry_t tss_entry;

// Función para configurar una entrada de la GDT
static void gdt_set_gate(int32_t num, uint32_t base, uint32_t limit, uint8_t access, uint8_t gran) {
    gdt_entries[num].base_low    = (base & 0xFFFF);
    gdt_entries[num].base_middle = (base >> 16) & 0xFF;
    gdt_entries[num].base_high   = (base >> 24) & 0xFF;

    gdt_entries[num].limit_low   = (limit & 0xFFFF);
    gdt_entries[num].granularity = (limit >> 16) & 0x0F;

    gdt_entries[num].granularity |= gran & 0xF0;
    gdt_entries[num].access      = access;
}

// Función para escribir la TSS
static void tss_write() {
    uint32_t base = (uint32_t)&tss_entry;
    uint32_t limit = sizeof(tss_entry);

    // Configurar la entrada de la GDT para la TSS (entrada 5)
    gdt_set_gate(5, base, limit, 0x89, 0x40); // 0x89: Present, Ring 0, System, TSS

    // Inicializar la TSS
    tss_entry.ss0  = 0x10; // Segmento de datos del kernel
    tss_entry.esp0 = 0;   // Se establecerá dinámicamente en cada cambio de tarea
    tss_entry.cs = 0x0b;
    tss_entry.ss = tss_entry.ds = tss_entry.es = tss_entry.fs = tss_entry.gs = 0x13;
}

// Función principal de inicialización
void gdt_init() {
    gdt_pointer.limit = (sizeof(gdt_entry_t) * 6) - 1;
    gdt_pointer.base  = (uint32_t)&gdt_entries;

    gdt_set_gate(0, 0, 0, 0, 0);                // 0x00: Segmento nulo
    gdt_set_gate(1, 0, 0xFFFFFFFF, 0x9A, 0xCF); // 0x08: Código de Kernel (Ring 0)
    gdt_set_gate(2, 0, 0xFFFFFFFF, 0x92, 0xCF); // 0x10: Datos de Kernel (Ring 0)
    gdt_set_gate(3, 0, 0xFFFFFFFF, 0xFA, 0xCF); // 0x18: Código de Usuario (Ring 3)
    gdt_set_gate(4, 0, 0xFFFFFFFF, 0xF2, 0xCF); // 0x20: Datos de Usuario (Ring 3)

    tss_write(); // 0x28: TSS

    gdt_flush((uint32_t)&gdt_pointer);
    tss_flush();
}