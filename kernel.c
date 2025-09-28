#include <stdint.h>
#include "keyboard.h"
#include "shell.h"
#include "multiboot2.h"
#include "pmm.h"
#include "heap.h"
#include "serial.h"
#include "task.h"

// --- Declaraciones de funciones ---
void idt_init();
void timer_init(uint32_t frequency);

// --- Funciones de pantalla y cadenas ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0;
int cursor_y = 0;

void screen_clear() {
    for (int i = 0; i < 80 * 25; i++) {
        video_memory[i * 2] = ' ';
    }
    cursor_x = 0;
    cursor_y = 0;
}

void kprint_char(char c) {
    // Escribir en la memoria de vídeo
    if (c == '\n') {
        cursor_y++;
        cursor_x = 0;
    } else {
        video_memory[(cursor_y * 80 + cursor_x) * 2] = c;
        cursor_x++;
    }
    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }
    // Escribir en el puerto serie
    serial_write_char(c);
}

void kprint(const char *str) {
    for(int i = 0; str[i]; i++) {
        kprint_char(str[i]);
    }
}

void itox(uint64_t n, char str[]) {
    char *c = "0123456789ABCDEF", temp[17];
    int i = 0, j = 0;
    if (n == 0) {
        str[0] = '0';
        str[1] = '\0';
        return;
    }
    while (n > 0) {
        temp[j++] = c[n % 16];
        n /= 16;
    }
    while (j > 0) {
        str[i++] = temp[--j];
    }
    str[i] = '\0';
}

void strcpy(char *dest, const char *src) {
    while ((*dest++ = *src++));
}

// --- Tareas de Prueba ---
void task_a_func() {
    kprint("\n[Tarea A iniciada]\n");
    for (;;) {
        kprint("A");
    }
}

void task_b_func() {
    kprint("\n[Tarea B iniciada]\n");
    for (;;) {
        kprint("B");
    }
}

// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    serial_init();
    screen_clear();
    kprint("CarleyOS v0.3 - Multitarea\n");

    if (magic != MULTIBOOT2_BOOTLOADER_MAGIC) {
        kprint("Error: Magico de Multiboot2 invalido.\n");
        return;
    }

    // Inicialización de la Memoria
    pmm_init(addr);
    heap_init();

    // Inicialización de la Multitarea
    kprint("Inicializando Multitarea... ");
    task_init();
    kprint("OK\n");

    kprint("Creando tareas de prueba...\n");
    task_create(task_a_func);
    task_create(task_b_func);

    kprint("\nInicializacion completa. Lanzando shell...\n");
    kprint("La multitarea apropiativa esta activa.\n\n");

    // Inicialización del resto de sistemas
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