#ifndef SHELL_H
#define SHELL_H

// Inicializa la shell.
void shell_init();

// Procesa una línea de comando recibida desde el teclado.
void shell_handle_line(const char *input);

#endif // SHELL_H