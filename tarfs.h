#ifndef TARFS_H
#define TARFS_H

#include <stdint.h>

/*
 * Inicializa el sistema de archivos tarfs desde una dirección de memoria.
 * Monta el contenido como el sistema de archivos raíz.
 */
void tarfs_init(uint32_t initrd_location);

#endif // TARFS_H