// shell.c - Un shell simple para CarleyOS

// Syscalls que usaremos
void print(const char* str) {
    asm volatile ("int $0x80" : : "a"(1), "b"(str));
}

void exec(const char* path) {
    asm volatile ("int $0x80" : : "a"(2), "b"(path));
}

void waitpid(int pid) {
    asm volatile ("int $0x80" : : "a"(4), "b"(pid));
}

void read(char* buffer) {
    asm volatile ("int $0x80" : : "a"(5), "b"(buffer));
}

// Función simple para comparar strings
int strcmp(const char* s1, const char* s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

int main() {
    char input_buffer[256];

    while (1) {
        print("> ");
        read(input_buffer);

        if (strcmp(input_buffer, "run /bin/hello") == 0) {
            print("Ejecutando hello...\n");
            exec("/bin/hello");
            waitpid(0); // Esperar a cualquier hijo
            print("\nhello ha terminado.\n");
        } else {
            print("Comando desconocido.\n");
        }
    }

    return 0;
}