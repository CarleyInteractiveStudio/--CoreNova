// hello.c - Nuestro primer programa de usuario.

int main() {
    // Este string está en el espacio de memoria del programa.
    const char* msg = "Hola desde un programa externo!";

    // Usamos ensamblador en línea para hacer la llamada al sistema.
    // EAX=1 (sys_print), EBX=puntero al mensaje.
    asm volatile ("int $0x80" : : "a"(1), "b"(msg));

    // Llamada al sistema para salir del programa.
    asm volatile ("int $0x80" : : "a"(3), "b"(0));

    return 0; // Esta línea nunca se alcanzará.
}