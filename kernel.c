#include <stdint.h>
#include "keyboard.h"
#include "shell.h"

// --- Declaraciones de funciones ---
void idt_init();
void timer_init(uint32_t frequency);
// keyboard_init() está en keyboard.h
// shell_init() y shell_handle_line() están en shell.h

// --- Funciones de pantalla ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0;
int cursor_y = 0;

void screen_clear() {
    for (int y = 0; y < 25; y++) {
        for (int x = 0; x < 80; x++) {
            video_memory[(y * 80 + x) * 2] = ' ';
            video_memory[(y * 80 + x) * 2 + 1] = 0x07;
        }
    }
    cursor_x = 0;
    cursor_y = 0;
}

void kprint_char(char c) {
    if (c == '\n') {
        cursor_y++;
        cursor_x = 0;
    } else if (c == '\b') {
        if (cursor_x > 0) {
            cursor_x--;
            video_memory[(cursor_y * 80 + cursor_x) * 2] = ' ';
            video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = 0x07;
        }
        // Opcional: manejar retroceso al principio de una línea
    } else {
        video_memory[(cursor_y * 80 + cursor_x) * 2] = c;
        video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = 0x07;
        cursor_x++;
    }

    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }

    // Scroll simple
    if (cursor_y >= 25) {
        // Mover todas las líneas una hacia arriba
        for (int i = 0; i < 24 * 80 * 2; i++) {
            video_memory[i] = video_memory[i + 80 * 2];
        }
        // Limpiar la última línea
        for (int i = 24 * 80; i < 25 * 80; i++) {
            video_memory[i * 2] = ' ';
            video_memory[i * 2 + 1] = 0x07;
        }
        cursor_y = 24;
    }
}

void kprint(const char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        kprint_char(str[i]);
    }
}

// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    (void)magic; (void)addr;

    // 1. Inicializar hardware básico
    idt_init();
    timer_init(100); // El timer sigue siendo útil para el futuro
    keyboard_init();

    // 2. Conectar el teclado a la shell
    keyboard_set_line_handler(shell_handle_line);

    // 3. Limpiar la pantalla e iniciar la shell
    screen_clear();
    shell_init();

    // 4. Habilitar interrupciones
    asm volatile("sti");

    // 5. Entrar en un bucle infinito. El trabajo se hace por interrupciones.
    for (;;) {
        asm volatile("hlt"); // Ahorra CPU mientras esperamos una interrupción
    }
}