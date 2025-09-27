#include <stdint.h>

// Declaraciones de funciones
void idt_init();
void timer_init(uint32_t frequency);
void keyboard_init();
extern volatile uint64_t ticks;

// --- Funciones de pantalla ---
volatile char *video_memory = (volatile char*)0xB8000;
int cursor_x = 0;
int cursor_y = 0;

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

void itoa(uint64_t n, char str[]) {
    int i = 0;
    if (n == 0) { str[i++] = '0'; str[i] = '\0'; return; }
    while (n != 0) { str[i++] = (n % 10) + '0'; n = n / 10; }
    str[i] = '\0';
    for (int j = 0; j < i / 2; j++) {
        char temp = str[j];
        str[j] = str[i - j - 1];
        str[i - j - 1] = temp;
    }
}

// --- Punto de entrada del Kernel ---
void kmain(unsigned long magic, unsigned long addr) {
    (void)magic; (void)addr;

    cursor_y = 5; cursor_x = 10;
    kprint("CarleyOS 64-bit Base Reconstruida con Exito!\n");

    idt_init();
    timer_init(100);
    keyboard_init();
    asm volatile("sti");

    kprint("Sistema de interrupciones listo. Puedes escribir.\n");

    uint64_t last_ticks = 0;
    char tick_str[20];

    for (;;) {
        if (ticks != last_ticks) {
            last_ticks = ticks;
            if (last_ticks % 100 == 0) {
                cursor_x = 0; cursor_y = 0;
                kprint("Uptime: ");
                itoa(last_ticks / 100, tick_str);
                kprint(tick_str);
                kprint("s   ");
            }
        }
    }
}