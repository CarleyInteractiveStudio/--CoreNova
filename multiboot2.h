#ifndef MULTIBOOT2_H
#define MULTIBOOT2_H

#include <stdint.h>

#define MULTIBOOT2_TAG_TYPE_END         0
#define MULTIBOOT2_TAG_TYPE_CMDLINE     1
#define MULTIBOOT2_TAG_TYPE_BOOT_LOADER 2
#define MULTIBOOT2_TAG_TYPE_MODULE      3
#define MULTIBOOT2_TAG_TYPE_BASIC_MEMINFO 4
#define MULTIBOOT2_TAG_TYPE_BOOTDEV     5
#define MULTIBOOT2_TAG_TYPE_MMAP        6
#define MULTIBOOT2_TAG_TYPE_VBE         7
#define MULTIBOOT2_TAG_TYPE_FRAMEBUFFER 8
#define MULTIBOOT2_TAG_TYPE_ELF_SECTIONS 9
#define MULTIBOOT2_TAG_TYPE_APM         10

#define MULTIBOOT2_MEMORY_AVAILABLE        1
#define MULTIBOOT2_MEMORY_RESERVED         2
#define MULTIBOOT2_MEMORY_ACPI_RECLAIMABLE 3
#define MULTIBOOT2_MEMORY_NVS              4
#define MULTIBOOT2_MEMORY_BADRAM           5

typedef struct multiboot2_tag {
    uint32_t type;
    uint32_t size;
} multiboot2_tag_t;

typedef struct multiboot2_mmap_entry {
    uint64_t base_addr;
    uint64_t length;
    uint32_t type;
    uint32_t reserved;
} multiboot2_mmap_entry_t;

typedef struct multiboot2_tag_mmap {
    uint32_t type;
    uint32_t size;
    uint32_t entry_size;
    uint32_t entry_version;
    multiboot2_mmap_entry_t entries[];
} multiboot2_tag_mmap_t;

#endif // MULTIBOOT2_H