#include "shell.h"
#include "task.h"
#include "fs.h"
#include <stdint.h>
#include <stddef.h> // Para size_t

// --- Declaraciones de funciones externas ---
extern void kprint(const char *str);
extern void kprint_char(char c);
extern void screen_clear();

// --- Funciones auxiliares de cadenas ---

int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

int strncmp(const char *s1, const char *s2, size_t n) {
    if (n == 0) return 0;
    while (n-- != 0 && *s1 == *s2) {
        if (n == 0 || *s1 == '\0') break;
        s1++;
        s2++;
    }
    return *(unsigned char *)s1 - *(unsigned char *)s2;
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
        kprint("  ls    - Lista los archivos del initrd\n");
        kprint("  cat [f] - Muestra el contenido del archivo [f]\n");
        kprint("  echo [t]- Repite el texto [t]\n");
        kprint("  reboot - Reinicia el sistema\n");
    } else if (strcmp(input, "ls") == 0) {
        fs_list_files();
    } else if (strcmp(input, "clear") == 0) {
        screen_clear();
    } else if (strcmp(input, "reboot") == 0) {
        asm volatile ("int $0x3");
    } else if (strncmp(input, "cat ", 4) == 0) {
        const char* filename = input + 4;
        uint32_t file_size = 0;
        char* content = fs_read_file(filename, &file_size);

        if (content != NULL) {
            for (uint32_t i = 0; i < file_size; i++) {
                kprint_char(content[i]);
            }
            kprint("\n");
        } else {
            kprint("Archivo no encontrado: ");
            kprint(filename);
            kprint("\n");
        }
    } else if (strncmp(input, "echo ", 5) == 0) {
        kprint(input + 5);
        kprint("\n");
    } else if (strcmp(input, "") == 0) {
        // No hacer nada
    } else {
        kprint("Comando desconocido: '");
        kprint(input);
        kprint("'\n");
    }
    kprint("> ");
}