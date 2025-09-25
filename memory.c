#include "memory.h"

// Suponemos una cantidad máxima de memoria para simplificar (ej: 128MB).
#define MAX_MEMORY_SIZE 0x8000000 // 128 MB
#define MAX_FRAMES (MAX_MEMORY_SIZE / FRAME_SIZE)
#define MEMORY_MAP_SIZE (MAX_FRAMES / 8) // 1 bit por marco, 8 bits por byte.

// Nuestro bitmap para llevar el registro de los marcos de memoria.
static uint8_t memory_map[MEMORY_MAP_SIZE];
static uint32_t total_frames;
static uint32_t first_available_frame;

// Funciones para manipular los bits del bitmap.
static void set_frame(uint32_t frame_idx) {
    memory_map[frame_idx / 8] |= (1 << (frame_idx % 8));
}

static void clear_frame(uint32_t frame_idx) {
    memory_map[frame_idx / 8] &= ~(1 << (frame_idx % 8));
}

/*
static int test_frame(uint32_t frame_idx) {
    return memory_map[frame_idx / 8] & (1 << (frame_idx % 8));
}
*/

void memory_init(uint32_t mem_size, uint32_t kernel_end) {
    total_frames = mem_size / FRAME_SIZE;

    // Marcar toda la memoria como ocupada inicialmente.
    for (uint32_t i = 0; i < MEMORY_MAP_SIZE; i++) {
        memory_map[i] = 0xFF;
    }

    // Calcular el primer marco libre después del kernel y el bitmap.
    uint32_t kernel_and_bitmap_end = kernel_end + MEMORY_MAP_SIZE;
    first_available_frame = (kernel_and_bitmap_end + FRAME_SIZE - 1) / FRAME_SIZE;

    // Liberar todos los marcos desde el final del kernel+bitmap hasta el final de la memoria.
    for (uint32_t i = first_available_frame; i < total_frames; i++) {
        clear_frame(i);
    }
}

uint32_t alloc_frame() {
    for (uint32_t i = first_available_frame; i < total_frames; i++) {
        // Encontrar el primer byte que no esté completamente lleno.
        if (memory_map[i / 8] != 0xFF) {
            // Encontrar el primer bit libre en ese byte.
            for (uint32_t j = 0; j < 8; j++) {
                uint32_t frame_idx = i * 8 + j;
                if (!(memory_map[frame_idx / 8] & (1 << (frame_idx % 8)))) {
                    set_frame(frame_idx);
                    return frame_idx * FRAME_SIZE;
                }
            }
        }
    }
    // TODO: Manejar el caso de no más memoria (kernel panic).
    return 0;
}

void free_frame(uint32_t frame_addr) {
    uint32_t frame_idx = frame_addr / FRAME_SIZE;
    clear_frame(frame_idx);
}