#ifndef MULTIBOOT2_H
#define MULTIBOOT2_H

#include <stdint.h>

#define MULTIBOOT2_HEADER_MAGIC         0xE85250D6
#define MULTIBOOT2_BOOTLOADER_MAGIC     0x36D76289

// --- Estructura de las etiquetas de información de arranque ---

struct multiboot_tag {
    uint32_t type;
    uint32_t size;
};

// --- Tipos de Etiquetas ---

#define MULTIBOOT_TAG_TYPE_END              0
#define MULTIBOOT_TAG_TYPE_CMDLINE          1
#define MULTIBOOT_TAG_TYPE_BOOT_LOADER_NAME 2
#define MULTIBOOT_TAG_TYPE_MODULE           3
#define MULTIBOOT_TAG_TYPE_BASIC_MEMINFO    4
#define MULTIBOOT_TAG_TYPE_BOOTDEV          5
#define MULTIBOOT_TAG_TYPE_MMAP             6
#define MULTIBOOT_TAG_TYPE_VBE              7
#define MULTIBOOT_TAG_TYPE_FRAMEBUFFER      8
#define MULTIBOOT_TAG_TYPE_ELF_SECTIONS     9
#define MULTIBOOT_TAG_TYPE_APM              10

// --- Estructuras de Etiquetas Específicas ---

// Etiqueta para Módulos (type = 3)
struct multiboot_tag_module {
    uint32_t type;
    uint32_t size;
    uint32_t mod_start;
    uint32_t mod_end;
    char cmdline[]; // El resto son los bytes de la cadena de nombre del módulo
};

// Etiqueta para el Mapa de Memoria (type = 6)
struct multiboot_tag_mmap {
    uint32_t type;
    uint32_t size;
    uint32_t entry_size;
    uint32_t entry_version;
    // Siguen las entradas del mapa de memoria
};

// Entrada individual en el mapa de memoria
struct multiboot_mmap_entry {
    uint64_t addr;
    uint64_t len;
    uint32_t type;
    uint32_t zero;
};

// Tipos de región de memoria en la entrada del mapa
#define MULTIBOOT_MEMORY_AVAILABLE          1
#define MULTIBOOT_MEMORY_RESERVED           2
#define MULTIBOOT_MEMORY_ACPI_RECLAIMABLE   3
#define MULTIBOOT_MEMORY_NVS                4
#define MULTIBOOT_MEMORY_BADRAM             5

#endif // MULTIBOOT2_H