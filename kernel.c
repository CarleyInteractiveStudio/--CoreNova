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

#include "memory.h" // Para memory_init
#include "paging.h" // Para paging_init
#include "kheap.h"  // Para kheap_init, kmalloc, kfree
#include <stddef.h> // Para NULL
#include "task.h"   // Para tasking_init, create_task

// Declaraciones de las funciones de inicialización que hemos creado.
void idt_init();
void keyboard_init();
void timer_init(unsigned int frequency);

extern volatile uint32_t ticks; // La variable de nuestro timer.c
extern uint32_t end; // Símbolo del linker.ld

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


void gdt_init();
void syscalls_init();

/*
 * Esta es la función principal de nuestro kernel, llamada desde boot.s
 */
void kmain(void) {
    clear_screen();
    kprint("Bienvenido a CarleyOS", 0);

    gdt_init();
    kprint("GDT y TSS cargadas.", 1);

    kprint("Cerebro en construcción...", 2);

    // Suponemos 16MB de memoria para este ejemplo.
    uint32_t mem_size = 16 * 1024 * 1024;
    memory_init(mem_size, (uint32_t)&end);

    paging_init();
    kprint("¡Paginacion activada!", 3);

    kheap_init();
    kprint("Heap inicializado.", 4);

    tasking_init();
    kprint("Tasking inicializado.", 5);

    // Prueba de kmalloc
    void* test_mem = kmalloc(128);
    if (test_mem != NULL) {
        kprint("kmalloc funciona!", 5);
        kfree(test_mem);
    } else {
        kprint("kmalloc fallo.", 5);
    }

    // Inicializar el sistema de interrupciones, el teclado, el temporizador y las syscalls.
    idt_init();
    syscalls_init();
    keyboard_init();
    timer_init(100); // Iniciar el temporizador a 100Hz

    // Habilitar las interrupciones. A partir de este punto, el sistema puede reaccionar.
    asm volatile ("sti");

    uint32_t last_ticks = 0;
    int seconds = 0;
    char seconds_str[12];

    // --- Tarea de prueba de Espacio de Usuario ---
    void user_test_task() {
        const char* msg = "Hola desde el espacio de usuario!";
        while(1) {
            // Llamada al sistema para imprimir
            asm volatile ("int $0x80" : : "a"(1), "b"(msg));
            for (volatile int i = 0; i < 10000000; i++); // Retardo
        }
    }

    create_task(user_test_task, 1); // 1 = es una tarea de usuario

    // El kernel ahora se convierte en la tarea 'idle'.
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