#ifndef PAGING_H
#define PAGING_H

#include <stdint.h>
#include "memory.h"

#define PAGE_PRESENT    0x1
#define PAGE_WRITE      0x2
#define PAGE_USER       0x4

// Estructura de una entrada de página (común para todos los niveles)
typedef struct {
    uint64_t present    : 1;
    uint64_t rw         : 1;
    uint64_t user       : 1;
    uint64_t accessed   : 1;
    uint64_t dirty      : 1;
    uint64_t unused     : 7;
    uint64_t frame      : 40; // El resto de los bits para la dirección del marco
    uint64_t reserved   : 11;
    uint64_t nx         : 1;   // No-execute bit
} __attribute__((packed)) page_entry_t;

// Cada tabla tiene 512 entradas
#define TABLE_ENTRIES 512

// Estructuras para cada nivel de la jerarquía de paginación
typedef struct {
    page_entry_t entries[TABLE_ENTRIES];
} __attribute__((aligned(FRAME_SIZE))) page_table_t;

typedef struct {
    page_table_t* tables[TABLE_ENTRIES];
} page_directory_t;

typedef struct {
    page_directory_t* directories[TABLE_ENTRIES];
} pdpt_t;

typedef struct {
    pdpt_t* pdpts[TABLE_ENTRIES];
} pml4_t;


// Inicializa la paginación para el kernel
void paging_init();

// Mapea una página virtual a una física
void map_page(uint64_t virt_addr, uint64_t phys_addr, uint64_t flags);

#endif // PAGING_H