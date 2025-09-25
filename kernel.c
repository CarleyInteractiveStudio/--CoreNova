/* kernel.c - El punto de entrada de nuestro kernel */

/*
 * Escribe un string en una posición específica de la pantalla.
 * La memoria de video en modo texto está en la dirección 0xB8000.
 * Cada celda de la pantalla consta de 2 bytes:
 *   - 1 byte para el código del carácter ASCII.
 *   - 1 byte para el atributo de color (ej: 0x07 es blanco sobre negro).
 */
void kprint(const char *str, int line) {
    volatile unsigned char *video_memory = (unsigned char *)0xB8000;
    int offset = line * 80 * 2; // 80 columnas, 2 bytes por caracter
    video_memory += offset;

    for (int i = 0; str[i] != '\0'; ++i) {
        *video_memory++ = str[i];
        *video_memory++ = 0x07; // Atributo de color: texto blanco, fondo negro.
    }
}

/*
 * Limpia la pantalla escribiendo espacios en blanco en toda la memoria de video.
 */
void clear_screen() {
    volatile unsigned char *video_memory = (unsigned char *)0xB8000;
    for (int i = 0; i < 80 * 25; i++) {
        *video_memory++ = ' ';
        *video_memory++ = 0x07;
    }
}

#include <stdint.h> // Para uint32_t

// Declaraciones de las funciones de inicialización que hemos creado.
void idt_init();
void keyboard_init();
void timer_init(unsigned int frequency);

extern volatile uint32_t ticks; // La variable de nuestro timer.c

// Función simple para convertir un número a string.
void itoa(int n, char str[]) {
    int i = 0;
    if (n == 0) {
        str[i++] = '0';
        str[i] = '\0';
        return;
    }
    int is_negative = 0;
    if (n < 0) {
        is_negative = 1;
        n = -n;
    }
    while (n != 0) {
        int rem = n % 10;
        str[i++] = rem + '0';
        n = n / 10;
    }
    if (is_negative) {
        str[i++] = '-';
    }
    str[i] = '\0';
    // Revertir el string
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


/*
 * Esta es la función principal de nuestro kernel, llamada desde boot.s
 */
void kmain(void) {
    clear_screen();
    kprint("Bienvenido a CarleyOS", 0);
    kprint("Ahora puedes escribir...", 2);

    // Inicializar el sistema de interrupciones, el teclado y el temporizador.
    idt_init();
    keyboard_init();
    timer_init(100); // Iniciar el temporizador a 100Hz

    // Habilitar las interrupciones. A partir de este punto, el sistema puede reaccionar.
    asm volatile ("sti");

    uint32_t last_ticks = 0;
    int seconds = 0;
    char seconds_str[12];

    // Bucle principal del kernel.
    while (1) {
        if (ticks >= last_ticks + 100) {
            last_ticks = ticks;
            seconds++;
            itoa(seconds, seconds_str);
            kprint("Uptime: ", 0);
            kprint("        ", 0); // Limpiar la zona
            kprint(seconds_str, 0);
        }
    }
}