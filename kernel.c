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

// Declaraciones de las funciones de inicialización que hemos creado.
void idt_init();
void keyboard_init();

/*
 * Esta es la función principal de nuestro kernel, llamada desde boot.s
 */
void kmain(void) {
    clear_screen();
    kprint("Bienvenido a CarleyOS", 0);
    kprint("Ahora puedes escribir...", 2);

    // Inicializar el sistema de interrupciones y el teclado.
    idt_init();
    keyboard_init();

    // Habilitar las interrupciones. A partir de este punto, el sistema puede reaccionar.
    asm volatile ("sti");

    // El kernel nunca debe terminar, así que entramos en un bucle infinito.
    // Las interrupciones seguirán funcionando en segundo plano.
    for (;;);
}