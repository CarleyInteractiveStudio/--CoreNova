#ifndef IDT_H
#define IDT_H

#include <stdint.h>

/*
 * Estructura de una entrada en la Tabla de Descriptores de Interrupciones (IDT).
 * Esta estructura debe tener un formato muy específico para que la CPU la entienda.
 */
typedef struct {
    uint16_t base_low;    // Los 16 bits inferiores de la dirección del manejador.
    uint16_t selector;    // Selector del segmento de código del kernel.
    uint8_t  always0;     // Este campo debe ser siempre cero.
    uint8_t  flags;       // Banderas de tipo y atributos.
    uint16_t base_high;   // Los 16 bits superiores de la dirección del manejador.
} __attribute__((packed)) idt_entry_t;

/*
 * Estructura del puntero a la IDT.
 * Esta estructura se carga en la CPU usando la instrucción 'lidt'.
 */
typedef struct {
    uint16_t limit;       // El tamaño de la tabla menos 1.
    uint32_t base;        // La dirección de memoria donde empieza la tabla.
} __attribute__((packed)) idt_ptr_t;

/*
 * Función para inicializar la IDT.
 */
void idt_init();

#endif // IDT_H