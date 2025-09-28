#include "shell.h"
#include "task.h"
#include <stdint.h>

// --- Declaraciones de funciones externas ---
extern void kprint(const char *str);
extern void kprint_char(char c); // Necesitaremos una función para imprimir un solo carácter
extern void screen_clear(); // Necesitaremos una función para limpiar la pantalla
extern volatile char *video_memory; // Para `screen_clear`

// --- Funciones auxiliares de cadenas ---

// Compara dos cadenas. Devuelve 0 si son iguales.
int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

// Encuentra la primera ocurrencia de un carácter en una cadena.
const char* strchr(const char* s, int c) {
    while (*s != (char)c) {
        if (!*s++) {
            return 0;
        }
    }
    return s;
}

// --- Implementación de la Shell ---

void shell_init() {
    kprint("CarleyOS Shell v0.1\n");
    kprint("Escribe 'help' para ver los comandos disponibles.\n");
    kprint("> ");
}

void shell_handle_line(const char *input) {
    if (strcmp(input, "help") == 0) {
        kprint("Comandos disponibles:\n");
        kprint("  help  - Muestra esta ayuda\n");
        kprint("  clear - Limpia la pantalla\n");
        kprint("  echo  - Repite el texto que le sigue\n");
        kprint("  reboot - Reinicia el sistema\n");
        kprint("  yield - Cede el control a otra tarea\n");
    } else if (strcmp(input, "clear") == 0) {
        screen_clear();
    } else if (strcmp(input, "yield") == 0) {
        schedule();
    } else if (strcmp(input, "reboot") == 0) {
        // Provocar una triple falta para reiniciar (método común en OS dev)
        asm volatile ("int $0x3");
    } else if (strcmp(input, "") == 0) {
        // No hacer nada si la línea está vacía
    }
    else {
        // Comprobar si es el comando "echo"
        const char *echo_cmd = "echo ";
        int is_echo = 1;
        for(int i=0; i<5; ++i) {
            if(input[i] != echo_cmd[i]) {
                is_echo = 0;
                break;
            }
        }

        if (is_echo && input[4] == ' ') {
            kprint(input + 5);
            kprint("\n");
        } else {
            kprint("Comando desconocido: '");
            kprint(input);
            kprint("'\n");
        }
    }
    kprint("> "); // Mostrar el prompt para el siguiente comando
}