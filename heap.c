#include "heap.h"
#include "pmm.h"
#include <stddef.h> // for NULL and size_t
#include <stdint.h>

// --- Estructuras y Variables Globales del Heap ---

// Cabecera para cada bloque de memoria en el heap.
// Se almacena justo antes de la memoria que se devuelve al usuario.
typedef struct block_header {
    size_t size;
    uint8_t is_free;
    struct block_header *next;
} block_header_t;

// Puntero al inicio de nuestra lista enlazada de bloques.
static block_header_t *heap_start = NULL;

// --- Implementación del Heap ---

void heap_init() {
    // Pedimos una página (4KB) al PMM para empezar nuestro heap.
    void* initial_heap_space = pmm_alloc_frame();
    if (initial_heap_space == NULL) {
        // No se pudo inicializar el heap, un problema grave.
        // En un kernel real, aquí se lanzaría un panic.
        return;
    }

    heap_start = (block_header_t*)initial_heap_space;
    heap_start->size = PAGE_SIZE - sizeof(block_header_t);
    heap_start->is_free = 1;
    heap_start->next = NULL;
}

void* kmalloc(size_t size) {
    if (size == 0) {
        return NULL;
    }

    block_header_t *current = heap_start;
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            // Encontramos un bloque adecuado. ¿Necesita ser dividido?
            // Dividimos si el espacio restante es suficiente para una nueva cabecera y algo de datos.
            if (current->size > size + sizeof(block_header_t)) {
                block_header_t *new_block = (block_header_t*)((uint8_t*)current + sizeof(block_header_t) + size);
                new_block->is_free = 1;
                new_block->size = current->size - size - sizeof(block_header_t);
                new_block->next = current->next;

                current->size = size;
                current->next = new_block;
            }

            current->is_free = 0;
            // Devolvemos un puntero al área de datos, que está justo después de la cabecera.
            return (void*)((uint8_t*)current + sizeof(block_header_t));
        }
        current = current->next;
    }

    // TODO: Si no hay espacio, podríamos pedir más páginas al PMM y expandir el heap.
    // Por ahora, simplemente fallamos.
    return NULL;
}

void kfree(void* ptr) {
    if (ptr == NULL) {
        return;
    }

    // Obtenemos el puntero a la cabecera desde el puntero de datos.
    block_header_t *block_to_free = (block_header_t*)((uint8_t*)ptr - sizeof(block_header_t));
    block_to_free->is_free = 1;

    // Intentar unir (coalesce) con el siguiente bloque si también está libre.
    if (block_to_free->next != NULL && block_to_free->next->is_free) {
        block_to_free->size += sizeof(block_header_t) + block_to_free->next->size;
        block_to_free->next = block_to_free->next->next;
    }

    // NOTA: Un `kfree` más avanzado también intentaría unirse con el bloque *anterior*.
    // Esto requeriría una lista doblemente enlazada o una búsqueda desde el principio.
    // Para nuestra implementación actual, esto es suficiente.
}