// hello.c - Nuestro primer programa de usuario.

int main() {
    // Este string está en el espacio de memoria del programa.
    const char* msg = "Hola desde un programa externo!";

    // Usamos ensamblador en línea para hacer la llamada al sistema.
    // EAX=1 (sys_print), EBX=puntero al mensaje.
    asm volatile ("int $0x80" : : "a"(1), "b"(msg));

    // Los programas de usuario deberían tener una syscall para salir.
    // Como no la tenemos, entramos en un bucle infinito.
    while(1);

    return 0;
}