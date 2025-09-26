#include "multiboot2.h"
#include <stdint.h>
#include <stddef.h>
#include "memory.h"
#include "paging.h"
#include "timer.h"
#include "idt.h"

// --- Funciones de pantalla (simplificadas) ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0, cursor_y = 0;

void kprint(const char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] == '\n') {
            cursor_y++;
            cursor_x = 0;
        } else {
            video_memory[(cursor_y * 80 + cursor_x) * 2] = str[i];
            video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = 0x07;
            cursor_x++;
        }
        if (cursor_x >= 80) {
            cursor_x = 0;
            cursor_y++;
        }
    }
}

// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    kprint("Bienvenido a CarleyOS 64-bit (Cerebro Pro Edition)!\n");

    if (magic != 0x36d76289) {
        kprint("Error: No se ha arrancado con Multiboot2.\n");
        for (;;);
    }

    // Buscar la etiqueta del mapa de memoria
    multiboot2_tag_mmap_t* mmap_tag = NULL;
    for (multiboot2_tag_t* tag = (multiboot2_tag_t*)(addr + 8);
         tag->type != MULTIBOOT2_TAG_TYPE_END;
         tag = (multiboot2_tag_t*)((uint8_t*)tag + ((tag->size + 7) & ~7))) {
        if (tag->type == MULTIBOOT2_TAG_TYPE_MMAP) {
            mmap_tag = (multiboot2_tag_mmap_t*)tag;
            break;
        }
    }

    if (!mmap_tag) {
        kprint("ERROR: No se encontro el mapa de memoria!\n");
        for (;;);
    }

    // Secuencia de inicialización
    memory_init(mmap_tag);
    kprint("Gestor de memoria fisica inicializado.\n");

    paging_init();
    kprint("Paginacion del kernel activada.\n");

    idt_init();
    timer_init(100);
    asm volatile("sti");
    kprint("Interrupciones y temporizador activados.\n");

    kprint("Inicializacion completa. Sistema estable.\n");

    for (;;) {
        asm ("hlt");
    }
}