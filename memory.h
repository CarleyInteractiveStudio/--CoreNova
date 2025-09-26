#ifndef MEMORY_H
#define MEMORY_H

#include <stdint.h>
#include "multiboot2.h"

#define FRAME_SIZE 0x1000 // 4KB

/*
 * Inicializa el gestor de memoria física usando el mapa de memoria de Multiboot2.
 */
void memory_init(multiboot2_tag_mmap_t* mmap_tag);

/*
 * Asigna un marco de memoria física de 4KB.
 * Devuelve la dirección física del marco asignado.
 */
uint64_t alloc_frame();

/*
 * Libera un marco de memoria física.
 * frame_addr: La dirección del marco a liberar.
 */
void free_frame(uint64_t frame_addr);

#endif // MEMORY_H