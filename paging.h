#ifndef PAGING_H
#define PAGING_H

#include <stdint.h>
#include "memory.h" // Para FRAME_SIZE

// Banderas para las entradas del directorio y de la tabla de páginas.
#define PAGE_PRESENT    0x1
#define PAGE_WRITE      0x2
#define PAGE_USER       0x4

// Una entrada en la tabla de páginas.
typedef struct {
    uint32_t present    : 1;   // La página está presente en memoria.
    uint32_t rw         : 1;   // 1=lectura/escritura, 0=solo lectura.
    uint32_t user       : 1;   // 1=accesible en modo usuario, 0=solo supervisor.
    uint32_t accessed   : 1;   // La CPU lo pone a 1 cuando se accede a la página.
    uint32_t dirty      : 1;   // La CPU lo pone a 1 cuando se escribe en la página.
    uint32_t unused     : 7;   // Bits no utilizados.
    uint32_t frame      : 20;  // Dirección del marco físico (alineado a 4KB).
} page_table_entry_t;

// Una entrada en el directorio de páginas.
typedef struct {
    uint32_t present    : 1;
    uint32_t rw         : 1;
    uint32_t user       : 1;
    uint32_t accessed   : 1;
    uint32_t dirty      : 1;
    uint32_t unused     : 7;
    uint32_t frame      : 20;
} page_directory_entry_t;

// Estructura del Directorio de Páginas.
// Debe estar alineado a 4KB.
typedef struct {
    page_table_entry_t tables[1024];
} page_table_t;

typedef struct {
    page_directory_entry_t entries[1024];
} __attribute__((aligned(FRAME_SIZE))) page_directory_t;

/*
 * Inicializa la paginación.
 */
void paging_init();

#endif // PAGING_H