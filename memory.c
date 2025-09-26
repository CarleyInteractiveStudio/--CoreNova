#include "memory.h"
#include <stddef.h> // Para NULL

// Definimos un tamaño máximo de memoria para el bitmap (ej: 4GB)
#define MAX_FRAMES (0x100000000 / FRAME_SIZE)
#define MEMORY_MAP_SIZE (MAX_FRAMES / 8)

static uint8_t* memory_map = NULL;
static uint64_t total_frames = 0;
static uint64_t first_available_frame = 0;

// Funciones para manipular los bits del bitmap
static void set_frame(uint64_t frame_idx) {
    memory_map[frame_idx / 8] |= (1 << (frame_idx % 8));
}

static void clear_frame(uint64_t frame_idx) {
    memory_map[frame_idx / 8] &= ~(1 << (frame_idx % 8));
}

void memory_init(struct multiboot2_tag_mmap* mmap_tag) {
    multiboot2_mmap_entry_t* mmap_entry;

    // 1. Encontrar el tamaño total de la memoria para calcular el tamaño del bitmap
    uint64_t highest_addr = 0;
    for (mmap_entry = mmap_tag->entries;
         (uint8_t*)mmap_entry < (uint8_t*)mmap_tag + mmap_tag->size;
         mmap_entry = (multiboot2_mmap_entry_t*)((uint8_t*)mmap_entry + mmap_tag->entry_size)) {
        uint64_t top_addr = mmap_entry->base_addr + mmap_entry->length;
        if (top_addr > highest_addr) {
            highest_addr = top_addr;
        }
    }
    total_frames = highest_addr / FRAME_SIZE;
    uint64_t bitmap_size = total_frames / 8;

    // 2. Encontrar un lugar para nuestro bitmap
    for (mmap_entry = mmap_tag->entries;
         (uint8_t*)mmap_entry < (uint8_t*)mmap_tag + mmap_tag->size;
         mmap_entry = (multiboot2_mmap_entry_t*)((uint8_t*)mmap_entry + mmap_tag->entry_size)) {
        if (mmap_entry->type == MULTIBOOT2_MEMORY_AVAILABLE && mmap_entry->length >= bitmap_size) {
            memory_map = (uint8_t*)mmap_entry->base_addr;
            break;
        }
    }

    // 3. Inicializar el bitmap (marcar todo como en uso)
    for (uint64_t i = 0; i < bitmap_size; i++) {
        memory_map[i] = 0xFF;
    }

    // 4. Liberar los marcos que están realmente disponibles
    for (mmap_entry = mmap_tag->entries;
         (uint8_t*)mmap_entry < (uint8_t*)mmap_tag + mmap_tag->size;
         mmap_entry = (multiboot2_mmap_entry_t*)((uint8_t*)mmap_entry + mmap_tag->entry_size)) {
        if (mmap_entry->type == MULTIBOOT2_MEMORY_AVAILABLE) {
            for (uint64_t i = 0; i < mmap_entry->length / FRAME_SIZE; i++) {
                clear_frame((mmap_entry->base_addr / FRAME_SIZE) + i);
            }
        }
    }

    // 5. Marcar los marcos del kernel y del bitmap como en uso
    // (Suponemos que el kernel está en el primer mega y el bitmap donde lo pusimos)
    uint32_t kernel_frames = (1024 * 1024) / FRAME_SIZE; // 1MB
    for (uint32_t i = 0; i < kernel_frames; i++) set_frame(i);
    for (uint64_t i = 0; i < bitmap_size / FRAME_SIZE; i++) set_frame(((uint64_t)memory_map / FRAME_SIZE) + i);
}

uint64_t alloc_frame() {
    for (uint64_t i = 0; i < total_frames / 8; i++) {
        if (memory_map[i] != 0xFF) {
            for (int j = 0; j < 8; j++) {
                if (!(memory_map[i] & (1 << j))) {
                    uint64_t frame_idx = i * 8 + j;
                    set_frame(frame_idx);
                    return frame_idx * FRAME_SIZE;
                }
            }
        }
    }
    return 0; // No hay memoria
}

void free_frame(uint64_t frame_addr) {
    uint64_t frame_idx = frame_addr / FRAME_SIZE;
    clear_frame(frame_idx);
}