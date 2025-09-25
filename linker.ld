/* linker.ld - Script de enlazador correcto para Multiboot2 en x86_64 */
ENTRY(_start)

SECTIONS
{
    . = 1M; /* Cargar en 1MB */
    _kernel_start = .;

    /* La sección .boot debe estar primero y alineada */
    .boot ALIGN(4K) :
    {
        KEEP(*(.multiboot_header))
    }

    .text ALIGN(4K) :
    {
        *(.text)
    }

    .rodata ALIGN(4K) :
    {
        *(.rodata)
    }

    .bss ALIGN(4K) :
    {
        *(.bss)
    }

    _kernel_end = .;
}