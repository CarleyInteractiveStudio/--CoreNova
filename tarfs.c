#include "tarfs.h"
#include "vfs.h"
#include "kheap.h"
#include <stddef.h> // Para NULL
#include <stdint.h>

// Estructura de la cabecera de un archivo tar
typedef struct {
    char name[100];
    char mode[8];
    char uid[8];
    char gid[8];
    char size[12];
    char mtime[12];
    char chksum[8];
    char typeflag;
} tar_header_t;

// Función para convertir un tamaño octal en string a un entero.
static uint32_t oct2bin(const char *str, int size) {
    int n = 0;
    const char *c = str;
    while (size-- > 0) {
        n *= 8;
        n += *c - '0';
        c++;
    }
    return n;
}

// Implementaciones de las funciones del VFS para tarfs
static uint32_t tarfs_read(fs_node_t *node, uint32_t offset, uint32_t size, uint8_t *buffer) {
    uint8_t *file_content = (uint8_t*)((tar_header_t*)node->inode + 1);
    if (offset + size > node->length) {
        size = node->length - offset;
    }
    // Copiar memoria (reemplazar con una futura implementación de memcpy)
    for (uint32_t i = 0; i < size; i++) {
        buffer[i] = file_content[offset + i];
    }
    return size;
}

void tarfs_init(uint32_t initrd_location) {
    tar_header_t *current_header = (tar_header_t*)initrd_location;

    // Crear el nodo raíz
    fs_root = (fs_node_t*)kmalloc(sizeof(fs_node_t));
    // strcpy(fs_root->name, "/"); // futura implementación
    fs_root->name[0] = '/'; fs_root->name[1] = '\0';
    fs_root->flags = 0x02; // Directorio
    fs_root->finddir = NULL; // TODO
    fs_root->readdir = NULL; // TODO

    while (current_header->name[0] != '\0') {
        uint32_t size = oct2bin(current_header->size, 11);

        // Crear un nodo para este archivo
        fs_node_t *node = (fs_node_t*)kmalloc(sizeof(fs_node_t));
        // strcpy(node->name, current_header->name); // futura implementación
        for (int i = 0; i < 100; i++) node->name[i] = current_header->name[i];

        node->length = size;
        node->inode = (uint32_t)current_header;
        node->read = &tarfs_read;

        // TODO: Añadir este nodo al árbol del VFS. Por ahora, lo dejamos plano.
        // Un finddir simple para la prueba.
        if (fs_root->finddir == NULL) {
             fs_root->finddir = (finddir_type_t)node; // Abuso de puntero para prueba simple
        }

        // Mover al siguiente header
        uint32_t next_header_addr = (uint32_t)current_header + sizeof(tar_header_t) + size;
        if ((next_header_addr % 512) != 0) {
            next_header_addr = (next_header_addr & 0xFFFFFE00) + 512;
        }
        current_header = (tar_header_t*)next_header_addr;
    }
}