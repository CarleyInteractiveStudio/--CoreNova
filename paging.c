#include "paging.h"
#include "memory.h"
#include <stddef.h> // Para NULL

// El directorio de páginas del kernel.
page_directory_t *kernel_directory = NULL;

// Función externa para cargar el directorio de páginas y activar la paginación.
extern void load_page_directory_and_enable_paging(page_directory_t *dir);

void paging_init() {
    // Asigna un marco para el directorio de páginas del kernel.
    kernel_directory = (page_directory_t*)alloc_frame();

    // Limpia el directorio.
    for (int i = 0; i < 1024; i++) {
        kernel_directory->entries[i].present = 0;
        kernel_directory->entries[i].rw = 0;
    }

    // Crear una tabla de páginas para el primer megabyte de memoria (donde está el kernel).
    page_table_t *first_page_table = (page_table_t*)alloc_frame();
    for (int i = 0; i < 1024; i++) {
        first_page_table->tables[i].present = 1;
        first_page_table->tables[i].rw = 1; // El kernel necesita poder escribir en su propia memoria.
        first_page_table->tables[i].user = 0; // Solo accesible por el kernel.
        first_page_table->tables[i].frame = i; // Mapeo de identidad (virtual 0x... apunta a físico 0x...)
    }

    // Añadir esta tabla de páginas al directorio de páginas del kernel.
    kernel_directory->entries[0].present = 1;
    kernel_directory->entries[0].rw = 1;
    kernel_directory->entries[0].user = 0;
    kernel_directory->entries[0].frame = (uint32_t)first_page_table >> 12; // La dirección debe estar alineada a 4K.

    // Cargar el directorio de páginas y activar la paginación.
    load_page_directory_and_enable_paging(kernel_directory);
}