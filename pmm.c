#include "pmm.h"
#include <stddef.h> // for NULL

// --- Variables Globales del Módulo ---
static uint8_t* bitmap = NULL;
static size_t total_pages = 0;
static size_t bitmap_size = 0;
extern void kprint(const char* str); // Para depuración

// --- Funciones del Mapa de Bits ---

// Establece un bit en el mapa de bits (lo marca como usado)
static void bitmap_set(size_t bit) {
    bitmap[bit / 8] |= (1 << (bit % 8));
}

// Limpia un bit en el mapa de bits (lo marca como libre)
static void bitmap_clear(size_t bit) {
    bitmap[bit / 8] &= ~(1 << (bit % 8));
}

// Prueba un bit en el mapa de bits
static uint8_t bitmap_test(size_t bit) {
    return bitmap[bit / 8] & (1 << (bit % 8));
}

// --- Implementación del PMM ---

void pmm_init(unsigned long multiboot_info_addr) {
    // 1. Encontrar la memoria total para calcular el tamaño del bitmap
    uint64_t highest_addr = 0;
    struct multiboot_tag *tag;
    for (tag = (struct multiboot_tag *)(multiboot_info_addr + 8);
         tag->type != MULTIBOOT_TAG_TYPE_END;
         tag = (struct multiboot_tag *)((uint8_t *)tag + ((tag->size + 7) & ~7))) {

        if (tag->type == MULTIBOOT_TAG_TYPE_MMAP) {
            struct multiboot_tag_mmap *mmap_tag = (struct multiboot_tag_mmap *)tag;
            struct multiboot_mmap_entry *entry;
            for (entry = (struct multiboot_mmap_entry *)(mmap_tag + 1);
                 (uint8_t *)entry < (uint8_t *)tag + tag->size;
                 entry = (struct multiboot_mmap_entry *)((uint8_t *)entry + mmap_tag->entry_size)) {
                if (entry->addr + entry->len > highest_addr) {
                    highest_addr = entry->addr + entry->len;
                }
            }
        }
    }
    total_pages = highest_addr / PAGE_SIZE;
    bitmap_size = total_pages / 8;
    if (bitmap_size * 8 < total_pages) bitmap_size++;

    // 2. Encontrar un lugar para nuestro bitmap
    for (tag = (struct multiboot_tag *)(multiboot_info_addr + 8);
         tag->type != MULTIBOOT_TAG_TYPE_END;
         tag = (struct multiboot_tag *)((uint8_t *)tag + ((tag->size + 7) & ~7))) {

        if (tag->type == MULTIBOOT_TAG_TYPE_MMAP) {
            struct multiboot_tag_mmap *mmap_tag = (struct multiboot_tag_mmap *)tag;
            struct multiboot_mmap_entry *entry;
            for (entry = (struct multiboot_mmap_entry *)(mmap_tag + 1);
                 (uint8_t *)entry < (uint8_t *)tag + tag->size;
                 entry = (struct multiboot_mmap_entry *)((uint8_t *)entry + mmap_tag->entry_size)) {

                // Buscamos una región disponible lo suficientemente grande
                if (entry->type == MULTIBOOT_MEMORY_AVAILABLE && entry->len >= bitmap_size) {
                    bitmap = (uint8_t*)entry->addr;
                    break;
                }
            }
        }
        if (bitmap != NULL) break;
    }

    if (bitmap == NULL) {
        kprint("Error: No se encontro memoria para el bitmap del PMM.\n");
        return;
    }

    // 3. Inicializar el bitmap: marcar todo como usado por defecto
    for (size_t i = 0; i < bitmap_size; i++) {
        bitmap[i] = 0xFF;
    }

    // 4. Marcar las regiones disponibles como libres
    for (tag = (struct multiboot_tag *)(multiboot_info_addr + 8);
         tag->type != MULTIBOOT_TAG_TYPE_END;
         tag = (struct multiboot_tag *)((uint8_t *)tag + ((tag->size + 7) & ~7))) {

        if (tag->type == MULTIBOOT_TAG_TYPE_MMAP) {
            struct multiboot_tag_mmap *mmap_tag = (struct multiboot_tag_mmap *)tag;
            struct multiboot_mmap_entry *entry;
            for (entry = (struct multiboot_mmap_entry *)(mmap_tag + 1);
                 (uint8_t *)entry < (uint8_t *)tag + tag->size;
                 entry = (struct multiboot_mmap_entry *)((uint8_t *)entry + mmap_tag->entry_size)) {

                if (entry->type == MULTIBOOT_MEMORY_AVAILABLE) {
                    for (uint64_t i = 0; i < entry->len; i += PAGE_SIZE) {
                        bitmap_clear((entry->addr + i) / PAGE_SIZE);
                    }
                }
            }
        }
    }

    // 5. Marcar la memoria usada por el propio bitmap como usada
    size_t bitmap_pages = bitmap_size / PAGE_SIZE;
    if (bitmap_size % PAGE_SIZE) bitmap_pages++;
    for (size_t i = 0; i < bitmap_pages; i++) {
        bitmap_set(((uint64_t)bitmap / PAGE_SIZE) + i);
    }

    // NOTA: También deberíamos marcar las páginas del kernel como usadas.
    // Por simplicidad, asumimos que el kernel está por debajo de 1MB y que el
    // mapa de memoria de GRUB ya lo marca como reservado.
}

void* pmm_alloc_frame() {
    for (size_t i = 0; i < total_pages; i++) {
        if (!bitmap_test(i)) {
            bitmap_set(i);
            return (void*)(i * PAGE_SIZE);
        }
    }
    return NULL; // No hay memoria libre
}

void pmm_free_frame(void* frame_addr) {
    size_t bit = (size_t)frame_addr / PAGE_SIZE;
    bitmap_clear(bit);
}