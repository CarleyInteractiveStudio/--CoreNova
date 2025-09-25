/* kernel.c - Kernel de 64 bits con temporizador */

#include <stdint.h>

// Declaraciones de funciones
void idt_init();
void timer_init(uint32_t frequency);
extern volatile uint64_t ticks;

// --- Funciones de pantalla ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0;
int cursor_y = 0;

void kprint_char(char c, int x, int y, char attr) {
    video_memory[(y * 80 + x) * 2] = c;
    video_memory[(y * 80 + x) * 2 + 1] = attr;
}

void kprint(const char *str) {
    int i = 0;
    while (str[i] != '\0') {
        kprint_char(str[i], cursor_x, cursor_y, 0x07);
        cursor_x++;
        if (cursor_x >= 80) {
            cursor_x = 0;
            cursor_y++;
        }
        i++;
    }
}

void itoa(uint64_t n, char str[]) {
    int i = 0;
    if (n == 0) {
        str[i++] = '0';
        str[i] = '\0';
        return;
    }
    while (n != 0) {
        uint64_t rem = n % 10;
        str[i++] = rem + '0';
        n = n / 10;
    }
    str[i] = '\0';
    // Revertir string
    int start = 0;
    int end = i - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    (void)magic;
    (void)addr;

    cursor_y = 10;
    cursor_x = 25;
    kprint("Bienvenido a CarleyOS 64-bit!");

    idt_init();
    timer_init(100); // Iniciar temporizador a 100Hz

    asm volatile("sti"); // Habilitar interrupciones

    uint64_t last_ticks = 0;
    char tick_str[20];

    for (;;) {
        if (ticks != last_ticks) {
            last_ticks = ticks;
            if (last_ticks % 100 == 0) {
                cursor_x = 0;
                cursor_y = 0;
                kprint("Uptime: ");
                itoa(last_ticks / 100, tick_str);
                kprint(tick_str);
                kprint("s   ");
            }
        }
    }
}