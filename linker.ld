/* linker.ld - Script del enlazador para nuestro kernel. */
ENTRY(_start)
OUTPUT_FORMAT(elf32-i386)

SECTIONS
{
    /* Empezar a cargar en la dirección de memoria 1MB. */
    . = 1M;

    /* Primero, la sección de texto del bootloader. */
    .text :
    {
        *(.multiboot)
        *(.text)
    }

    /* Datos de solo lectura. */
    .rodata :
    {
        *(.rodata)
    }

    /* Datos inicializados. */
    .data :
    {
        *(.data)
    }

    /* Datos no inicializados (BSS). */
    .bss :
    {
        *(COMMON)
        *(.bss)
    }

    /* El símbolo 'end' marcará el final de nuestro kernel. */
    end = .;
}