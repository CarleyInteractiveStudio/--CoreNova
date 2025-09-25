/* user/link.ld - Script de enlazador para programas de usuario. */
ENTRY(main)
OUTPUT_FORMAT(elf32-i386)

SECTIONS
{
    . = 0x400000;

    .text :
    {
        *(.text)
    }

    .rodata :
    {
        *(.rodata)
    }

    .data :
    {
        *(.data)
    }

    .bss :
    {
        *(.bss)
    }
}