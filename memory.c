#include "memory.h"
#include <stddef.h> // Para NULL

// Puntero al bitmap. Se asignará dinámicamente.
static uint8_t* memory_map = NULL;
static uint64_t total_frames = 0;

// Funciones para manipular los bits del bitmap
static void set_frame(uint64_t frame_idx) {
    if (memory_map == NULL || frame_idx >= total_frames) return;
    memory_map[frame_idx / 8] |= (1 << (frame_idx % 8));
}

static void clear_frame(uint64_t frame_idx) {
    if (memory_map == NULL || frame_idx >= total_frames) return;
    memory_map[frame_idx / 8] &= ~(1 << (frame_idx % 8));
}

static uint8_t test_frame(uint64_t frame_idx) {
    if (memory_map == NULL || frame_idx >= total_frames) return 1; // Considerar no existente como ocupado
    return (memory_map[frame_idx / 8] & (1 << (frame_idx % 8))) != 0;
}

void memory_init(multiboot2_tag_mmap_t* mmap_tag) {
    multiboot2_mmap_entry_t* mmap_entry;

    // 1. Encontrar el tamaño total de la memoria
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

    // 5. Marcar los marcos del kernel (primer MB) y del bitmap como en uso
    uint32_t kernel_frames = (1024 * 1024) / FRAME_SIZE;
    for (uint32_t i = 0; i < kernel_frames; i++) set_frame(i);
    for (uint64_t i = 0; i < (bitmap_size + FRAME_SIZE -1) / FRAME_SIZE; i++) {
        set_frame(((uint64_t)memory_map / FRAME_SIZE) + i);
    }
}

uint64_t alloc_frame() {
    for (uint64_t i = 0; i < total_frames; i++) {
        if (!test_frame(i)) {
            set_frame(i);
            return i * FRAME_SIZE;
        }
    }
    return 0; // No hay memoria
}

void free_frame(uint64_t frame_addr) {
    uint64_t frame_idx = frame_addr / FRAME_SIZE;
    clear_frame(frame_idx);
}