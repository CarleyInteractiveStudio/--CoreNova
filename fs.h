#ifndef FS_H
#define FS_H

#include <stdint.h>

// --- Estructura de la Cabecera TAR (simplificada) ---
// La cabecera TAR tiene 512 bytes.
typedef struct {
    char filename[100];
    char mode[8];
    char uid[8];
    char gid[8];
    char size[12]; // Tamaño en bytes (cadena octal)
    char mtime[12];
    char chksum[8];
    char typeflag;
    // ... otros campos que ignoraremos por ahora ...
} tar_header_t;

// --- Interfaz del Sistema de Archivos ---

// Inicializa el sistema de archivos (basado en el initrd).
void fs_init();

// Lista los archivos en el initrd y los imprime en la consola.
void fs_list_files();

// Busca un archivo por su nombre y devuelve un puntero a su contenido.
// También escribe el tamaño del archivo en la variable `size`.
// Devuelve NULL si el archivo no se encuentra.
char* fs_read_file(const char* filename, uint32_t* size);

#endif // FS_H