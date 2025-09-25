/* kernel.c - El punto de entrada de nuestro kernel */

// Posición actual del cursor
int cursor_x = 0;
int cursor_y = 0;

void kprint(const char *str, int line) {
    volatile unsigned char *video_memory = (unsigned char *)0xB8000;

    if (line != -1) {
        cursor_x = 0;
        cursor_y = line;
    }

    int i = 0;
    while (str[i] != '\0') {
        if (str[i] == '\n') {
            cursor_y++;
            cursor_x = 0;
        } else if (str[i] == '\b') {
            if (cursor_x > 0) {
                cursor_x--;
                video_memory[(cursor_y * 80 + cursor_x) * 2] = ' ';
            }
        } else {
            video_memory[(cursor_y * 80 + cursor_x) * 2] = str[i];
            video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = 0x07;
            cursor_x++;
        }

        if (cursor_x >= 80) {
            cursor_x = 0;
            cursor_y++;
        }
        i++;
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
#include "tarfs.h"  // Para tarfs_init

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
void kmain(uint32_t mboot_ptr, uint32_t initrd_addr) {
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

    // Montar el sistema de archivos initrd.
    tarfs_init(initrd_addr);
    kprint("Initrd montado como sistema de archivos.", 6);

    // --- Tarea Init ---
    // Esta tarea del kernel simplemente lanzará el primer programa de usuario: el shell.
    void init_task() {
        const char* path = "/bin/shell";
        asm volatile ("int $0x80" : : "a"(2), "b"(path));
        // Esta tarea terminará después de lanzar el shell.
        // En un sistema real, aquí se implementaría una syscall de 'exit'.
    }

    create_task(init_task, 0); // 0 = es una tarea de kernel

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