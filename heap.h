#ifndef HEAP_H
#define HEAP_H

#include <stddef.h> // Para size_t

// Inicializa el heap del kernel.
void heap_init();

// Asigna un bloque de memoria del tamaño especificado.
void* kmalloc(size_t size);

// Libera un bloque de memoria previamente asignado.
void kfree(void* ptr);

#endif // HEAP_H