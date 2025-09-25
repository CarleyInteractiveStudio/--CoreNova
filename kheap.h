#ifndef KHEAP_H
#define KHEAP_H

#include <stdint.h>

// Funciones públicas
void kheap_init();
void* kmalloc(uint32_t size);
void kfree(void* ptr);

// Estructura del encabezado de un bloque de memoria
typedef struct {
    uint32_t magic;      // Número mágico para verificar la integridad
    uint8_t is_free;     // 1 si el bloque está libre, 0 si está ocupado
    uint32_t size;       // Tamaño del bloque, incluyendo el header y el footer
} header_t;

// Estructura del pie de página de un bloque de memoria
typedef struct {
    uint32_t magic;      // Número mágico, igual que en el header
    header_t* header;    // Puntero al header del bloque
} footer_t;

#endif // KHEAP_H