#include <stdint.h>
#include "keyboard.h"
#include "shell.h"
#include "multiboot2.h"
#include "pmm.h"
#include "heap.h"
#include "serial.h"

// --- Declaraciones de funciones ---
void idt_init();
void timer_init(uint32_t frequency);

// --- Funciones de pantalla y cadenas ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0;
int cursor_y = 0;

void screen_clear() {
    for (int y = 0; y < 25; y++) for (int x = 0; x < 80; x++) {
        video_memory[(y * 80 + x) * 2] = ' ';
        video_memory[(y * 80 + x) * 2 + 1] = 0x07;
    }
    cursor_x = 0;
    cursor_y = 0;
}

void kprint_char(char c) {
    // Escribir en la memoria de vídeo (pantalla)
    if (c == '\n') {
        cursor_y++;
        cursor_x = 0;
    } else if (c == '\b') {
        if (cursor_x > 0) {
            cursor_x--;
            video_memory[(cursor_y * 80 + cursor_x) * 2] = ' ';
        }
    } else {
        video_memory[(cursor_y * 80 + cursor_x) * 2] = c;
        video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = 0x07;
        cursor_x++;
    }
    if (cursor_x >= 80) { cursor_x = 0; cursor_y++; }
    if (cursor_y >= 25) {
        for (int i = 0; i < 24 * 80 * 2; i++) video_memory[i] = video_memory[i + 80 * 2];
        for (int i = 24 * 80; i < 25 * 80; i++) video_memory[i * 2] = ' ';
        cursor_y = 24;
    }

    // Escribir en el puerto serie
    serial_write_char(c);
}

void kprint(const char *str) {
    for (int i = 0; str[i] != '\0'; i++) kprint_char(str[i]);
}

void itox(uint64_t n, char str[]) {
    char *c = "0123456789ABCDEF";
    int i = 0;
    if (n == 0) { str[i++] = '0'; str[i] = '\0'; return; }
    char temp[17];
    int j = 0;
    while(n > 0) { temp[j++] = c[n % 16]; n /= 16; }
    temp[j] = '\0';
    while(j > 0) str[i++] = temp[--j];
    str[i] = '\0';
}

void strcpy(char *dest, const char *src) {
    int i = 0;
    while (src[i] != '\0') {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
}


// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    // Inicializar el puerto serie lo antes posible para la depuración.
    serial_init();

    screen_clear();
    kprint("CarleyOS v0.2 - Inicializando...\n");

    if (magic != MULTIBOOT2_BOOTLOADER_MAGIC) {
        kprint("Error: Magico de Multiboot2 invalido.\n");
        return;
    }

    // --- Inicialización de la Memoria ---
    kprint("Inicializando PMM... ");
    pmm_init(addr);
    kprint("OK\n");

    kprint("Inicializando Heap... ");
    heap_init();
    kprint("OK\n");

    // --- Prueba del Heap ---
    kprint("Probando kmalloc... ");
    char* test_str = kmalloc(25);
    if (test_str) {
        strcpy(test_str, "Hola desde kmalloc!");
        kprint("\n  -> Mensaje asignado: '");
        kprint(test_str);
        kprint("'\n");
        kfree(test_str);
        kprint("  -> Memoria liberada. Prueba OK.\n");
    } else {
        kprint("Fallo!\n");
    }

    kprint("\nInicializacion completa. Lanzando shell...\n\n");

    // --- Inicialización del resto de sistemas ---
    idt_init();
    timer_init(100);
    keyboard_init();
    keyboard_set_line_handler(shell_handle_line);

    shell_init();

    asm volatile("sti");
    for (;;) {
        asm volatile("hlt");
    }
}