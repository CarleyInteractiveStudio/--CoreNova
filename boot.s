; boot.s - Cargador de arranque de 64 bits para Multiboot2
; Maneja la transición de modo protegido de 32 bits a modo largo de 64 bits.

; --- Encabezado Multiboot2 ---
section .multiboot_header
align 8
header_start:
    dd 0xE85250D6                ; Número mágico de Multiboot2
    dd 0                         ; Arquitectura: i386 (modo protegido)
    dd header_end - header_start ; Longitud del encabezado
    dd -(0xE85250D6 + 0 + (header_end - header_start)) ; Suma de comprobación
    ; La etiqueta de fin es requerida
    dw 0, 0, 8
header_end:

; --- Sección BSS (datos no inicializados) ---
section .bss
align 4096
pml4:
    resb 4096
pdpt:
    resb 4096
pd0:
    resb 4096
stack_bottom:
    resb 16384 ; 16 KiB de pila
stack_top:

; --- Sección de Texto (código ejecutable) ---
section .text
global _start
extern kmain

_start:
    bits 32
    ; La CPU está en modo protegido de 32 bits.
    ; EAX = Mágico de Multiboot2
    ; EBX = Puntero a la estructura de información de Multiboot2

    ; Configurar una pila temporal
    mov esp, stack_top

    ; Guardar la información de Multiboot
    push eax
    push ebx

    ; Configurar tablas de página para mapear la primera 1GiB
    ; PML4[0] -> PDPT
    lea eax, [pdpt]
    or eax, 0b11 ; Presente, Lectura/Escritura
    mov [pml4], eax

    ; PDPT[0] -> PD0
    lea eax, [pd0]
    or eax, 0b11 ; Presente, Lectura/Escritura
    mov [pdpt], eax

    ; PD0 mapea la primera 1GiB usando páginas de 2MiB
    mov ecx, 0
.map_pd_loop:
    ; eax = (2MiB * ecx) | flags
    mov eax, 2 * 1024 * 1024
    mul ecx
    or eax, 0b10000011 ; Presente, Lectura/Escritura, Página Enorme
    mov [pd0 + ecx * 8], eax
    inc ecx
    cmp ecx, 512
    jne .map_pd_loop

    ; Cargar la dirección de PML4 en CR3
    mov eax, pml4
    mov cr3, eax

    ; Habilitar PAE
    mov eax, cr4
    or eax, 1 << 5
    mov cr4, eax

    ; Habilitar Modo Largo (LME) en el MSR EFER
    mov ecx, 0xC0000080
    rdmsr
    or eax, 1 << 8
    wrmsr

    ; Habilitar paginación
    mov eax, cr0
    or eax, 1 << 31
    mov cr0, eax

    ; Cargar GDT de 64 bits
    lgdt [gdt64.pointer]

    ; Saltar al segmento de código de 64 bits (selector 0x8)
    jmp 8:long_mode_start

; GDT para Modo Largo
gdt64:
    ; Descriptor nulo
    .null_descriptor:
        dq 0
    ; Descriptor de segmento de código
    .code_segment: equ $ - gdt64.null_descriptor
        dw 0xFFFF      ; límite
        dw 0           ; base
        db 0           ; base
        db 10011010b   ; flags (presente, anillo 0, código, ejecutable, legible)
        db 10101111b   ; flags (granularidad, 64 bits)
        db 0           ; base
    .pointer:
        dw $ - gdt64 - 1 ; límite
        dq gdt64         ; base

bits 64
long_mode_start:
    ; Ahora estamos en Modo Largo de 64 bits

    ; Recargar registros de segmento
    mov ax, 0 ; Usar descriptor nulo para los segmentos de datos
    mov ss, ax
    mov ds, ax
    mov es, ax

    ; Configurar la pila final
    mov rsp, stack_top

    ; Llamar al kernel en C
    pop rsi ; Puntero a la info de Multiboot
    pop rdi ; Mágico de Multiboot
    call kmain

    ; Colgar si kmain retorna
    cli
.hang:
    hlt
    jmp .hang