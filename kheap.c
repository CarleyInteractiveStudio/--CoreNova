#include "kheap.h"
#include "memory.h" // Para alloc_frame
#include <stddef.h> // Para NULL

#define KHEAP_MAGIC 0xDEADBEEF

// El inicio y el final del heap.
extern uint32_t end; // Definido en linker.ld
uint32_t kheap_start = (uint32_t)&end;
uint32_t kheap_end = (uint32_t)&end;

// Lista ordenada de bloques libres.
header_t* free_list_head = NULL;

void kheap_init() {
    // Por ahora, el heap no se puede expandir.
    // Simplemente alineamos el inicio del heap a una página.
    if ((kheap_start & 0xFFFFF000) != kheap_start) {
        kheap_start = (kheap_start & 0xFFFFF000) + FRAME_SIZE;
    }
    kheap_end = kheap_start; // El heap empieza vacío.
}

void* kmalloc(uint32_t size) {
    // Alinear el tamaño y añadir el tamaño del header y footer.
    uint32_t total_size = size + sizeof(header_t) + sizeof(footer_t);
    if ((total_size & 0xFFFFF000) != total_size) { // Alinear a 4k para simplificar
        total_size = (total_size & 0xFFFFF000) + FRAME_SIZE;
    }

    // Buscar un bloque libre lo suficientemente grande (First-fit).
    header_t* current = free_list_head;
    header_t* parent = NULL;
    while (current) {
        if (current->size >= total_size) {
            // ¡Bloque encontrado!
            // Por ahora, no lo dividimos para mantenerlo simple.
            // Lo quitamos de la lista de libres.
            if (parent) {
                parent->magic = (uint32_t)current->magic; // En C, usamos un campo del header como 'next'
            } else {
                free_list_head = (header_t*)current->magic;
            }
            current->is_free = 0;
            // Devolver un puntero al área de datos del usuario.
            return (void*)((uint32_t)current + sizeof(header_t));
        }
        parent = current;
        current = (header_t*)current->magic; // 'magic' se usa como 'next' en la lista de libres
    }

    // Si no se encontró un bloque, expandir el heap.
    uint32_t new_block_addr = kheap_end;
    kheap_end += total_size;

    header_t* header = (header_t*)new_block_addr;
    header->magic = KHEAP_MAGIC;
    header->is_free = 0;
    header->size = total_size;

    footer_t* footer = (footer_t*)(new_block_addr + total_size - sizeof(footer_t));
    footer->magic = KHEAP_MAGIC;
    footer->header = header;

    return (void*)((uint32_t)header + sizeof(header_t));
}

void kfree(void* ptr) {
    if (!ptr) {
        return;
    }

    // Obtener el header a partir del puntero del usuario.
    header_t* header = (header_t*)((uint32_t)ptr - sizeof(header_t));

    // Verificar la integridad.
    if (header->magic != KHEAP_MAGIC) {
        // Kernel panic! Corrupción del heap.
        return;
    }

    header->is_free = 1;

    // TODO: Implementar la fusión (coalescing) y añadir a la lista de libres.
    // Por ahora, simplemente lo marcamos como libre.
}