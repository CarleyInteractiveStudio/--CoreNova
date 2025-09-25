#ifndef MEMORY_H
#define MEMORY_H

#include <stdint.h>

#define FRAME_SIZE 0x1000 // 4KB

/*
 * Inicializa el administrador de memoria física.
 * mem_size: El tamaño total de la memoria en bytes.
 * kernel_end: La dirección donde termina el código del kernel.
 */
void memory_init(uint32_t mem_size, uint32_t kernel_end);

/*
 * Asigna un marco de memoria física de 4KB.
 * Devuelve la dirección física del marco asignado.
 */
uint32_t alloc_frame();

/*
 * Libera un marco de memoria física.
 * frame_addr: La dirección del marco a liberar.
 */
void free_frame(uint32_t frame_addr);

#endif // MEMORY_H