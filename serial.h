#ifndef SERIAL_H
#define SERIAL_H

// Inicializa el puerto serie COM1.
void serial_init();

// Escribe un único carácter en el puerto serie.
void serial_write_char(char c);

#endif // SERIAL_H