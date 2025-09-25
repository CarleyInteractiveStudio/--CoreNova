#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

// Inicializa el Temporizador de Intervalos Programable (PIT)
void timer_init(uint32_t frequency);

#endif // TIMER_H