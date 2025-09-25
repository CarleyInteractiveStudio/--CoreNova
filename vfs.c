#include "vfs.h"
#include <stddef.h> // Para NULL

fs_node_t *fs_root = NULL; // Se inicializará por el controlador del sistema de archivos

uint32_t read_fs(fs_node_t *node, uint32_t offset, uint32_t size, uint8_t *buffer) {
    if (node->read != NULL) {
        return node->read(node, offset, size, buffer);
    } else {
        return 0;
    }
}

uint32_t write_fs(fs_node_t *node, uint32_t offset, uint32_t size, uint8_t *buffer) {
    if (node->write != NULL) {
        return node->write(node, offset, size, buffer);
    } else {
        return 0;
    }
}

void open_fs(fs_node_t *node, uint8_t read, uint8_t write) {
    if (node->open != NULL) {
        node->open(node);
    }
}

void close_fs(fs_node_t *node) {
    if (node->close != NULL) {
        node->close(node);
    }
}

struct dirent *readdir_fs(fs_node_t *node, uint32_t index) {
    if ((node->flags & 0x7) == 0x02 && node->readdir != NULL) { // 0x02: Directorio
        return node->readdir(node, index);
    } else {
        return NULL;
    }
}

fs_node_t *finddir_fs(fs_node_t *node, char *name) {
    if ((node->flags & 0x7) == 0x02 && node->finddir != NULL) { // 0x02: Directorio
        return node->finddir(node, name);
    } else {
        return NULL;
    }
}