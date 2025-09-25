/* kernel.c - Kernel mínimo de 64 bits (Multiboot2) */

// Escribe un string en la memoria de video.
void kprint(const char *str) {
    // La memoria de video en modo texto está en 0xB8000.
    // El kernel de 64 bits puede acceder a esta dirección directamente.
    volatile char *video_memory = (volatile char*)0xB8000;
    while (*str != 0) {
        *video_memory++ = *str++;
        *video_memory++ = 0x07; // Atributo: texto blanco, fondo negro.
    }
}

// El punto de entrada del kernel, llamado desde boot.s
void kmain(unsigned long magic, unsigned long addr) {
    (void)magic; // Ignorar por ahora
    (void)addr;  // Ignorar por ahora

    kprint("Bienvenido a CarleyOS 64-bit (Multiboot2)!");

    // El kernel nunca debe terminar.
    for (;;) {
        asm ("hlt");
    }
}