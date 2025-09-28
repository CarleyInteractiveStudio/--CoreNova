#include "fs.h"
#include "heap.h"
#include <stddef.h>

// --- Declaraciones Externas ---
extern uintptr_t initrd_start; // Dirección de inicio del initrd, desde kernel.c
extern void kprint(const char *str);
extern int strcmp(const char *s1, const char *s2);

// --- Funciones Auxiliares ---

// Convierte un número octal en formato de cadena (de la cabecera TAR) a un entero.
static uint32_t tar_parse_octal(char *str, size_t size) {
    uint32_t n = 0;
    char *c = str;
    while (size-- > 0) {
        n *= 8;
        n += *c - '0';
        c++;
    }
    return n;
}

// --- Implementación de la Interfaz del Sistema de Archivos ---

void fs_init() {
    // Por ahora no es necesario hacer nada. El initrd ya está en memoria.
    // Simplemente comprobamos si fue cargado.
    if (initrd_start == 0) {
        kprint("Error: initrd no fue cargado por el bootloader.\n");
    }
}

void fs_list_files() {
    if (initrd_start == 0) return;

    uintptr_t current_addr = initrd_start;
    kprint("Archivos en initrd:\n");

    while (1) {
        tar_header_t *header = (tar_header_t*)current_addr;

        // El final del archivo TAR se marca con dos bloques de 512 bytes llenos de ceros.
        // Comprobamos si el nombre del archivo está vacío.
        if (header->filename[0] == '\0') {
            break;
        }

        uint32_t size = tar_parse_octal(header->size, 11);

        kprint(" - ");
        kprint(header->filename);
        kprint("\n");

        // Avanzar a la siguiente cabecera.
        // El contenido del archivo está alineado a 512 bytes.
        current_addr += sizeof(tar_header_t) + size;
        if (current_addr % 512 != 0) {
            current_addr += 512 - (current_addr % 512);
        }
    }
}

char* fs_read_file(const char* filename, uint32_t* size_out) {
    if (initrd_start == 0) return NULL;

    uintptr_t current_addr = initrd_start;

    while (1) {
        tar_header_t *header = (tar_header_t*)current_addr;

        if (header->filename[0] == '\0') {
            break; // Fin del archivo
        }

        uint32_t size = tar_parse_octal(header->size, 11);

        if (strcmp(header->filename, filename) == 0) {
            *size_out = size;
            // El contenido del archivo comienza justo después de la cabecera de 512 bytes.
            return (char*)(current_addr + sizeof(tar_header_t));
        }

        current_addr += sizeof(tar_header_t) + size;
        if (current_addr % 512 != 0) {
            current_addr += 512 - (current_addr % 512);
        }
    }

    return NULL; // Archivo no encontrado
}