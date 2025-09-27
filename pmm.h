#ifndef PMM_H
#define PMM_H

#include <stdint.h>
#include "multiboot2.h"

#define PAGE_SIZE 4096

// Inicializa el Administrador de Memoria Física.
// Necesita el puntero a la estructura de información de Multiboot para encontrar la memoria disponible.
void pmm_init(unsigned long multiboot_info_addr);

// Asigna un único marco de memoria física (4KB).
// Devuelve la dirección física del marco asignado, o 0 si no hay memoria libre.
void* pmm_alloc_frame();

// Libera un marco de memoria física previamente asignado.
void pmm_free_frame(void* frame_addr);

#endif // PMM_H