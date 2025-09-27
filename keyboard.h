#ifndef KEYBOARD_H
#define KEYBOARD_H

#include <stdint.h>

// Definición de un tipo para el manejador de línea.
// Esta es una función que toma una cadena (const char*) y no devuelve nada.
typedef void (*line_handler_t)(const char*);

// Inicializa el controlador del teclado
void keyboard_init();

// Establece la función que se llamará cuando se presione Enter.
void keyboard_set_line_handler(line_handler_t handler);

#endif // KEYBOARD_H