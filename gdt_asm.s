; gdt.s - Funciones de bajo nivel para cargar la GDT y la TSS.

global gdt_flush
extern gdt_pointer

gdt_flush:
    lgdt [esp+4]      ; Carga el puntero a nuestra GDT.
    mov ax, 0x10      ; 0x10 es el offset de nuestro segmento de datos del kernel.
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    jmp 0x08:.flush   ; 0x08 es el offset del segmento de código. Jmp para recargar CS.
.flush:
    ret


global tss_flush
tss_flush:
    mov ax, 0x28      ; 0x28 es el offset de nuestra entrada TSS en la GDT.
    ltr ax
    ret