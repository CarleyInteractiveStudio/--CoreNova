#include "syscall.h"
#include "idt.h"
#include "task.h" // Para la estructura regs_t

// Declaraciones de funciones externas
extern void syscall_interrupt_handler();
extern void kprint(const char *str, int line);
void idt_set_gate(uint8_t num, uint32_t base, uint16_t selector, uint8_t flags);

// Nuestra primera llamada al sistema: imprimir un string.
static void sys_print(const char* message) {
    // TODO: Deberíamos verificar que el puntero 'message'
    // pertenece al espacio de usuario antes de desreferenciarlo.
    kprint(message, 15); // Imprimir en la línea 15 para la prueba.
}

#include "vfs.h"
#include "kheap.h"

// Declaración de funciones externas
extern fs_node_t* finddir_fs(fs_node_t *node, char *name);
extern uint32_t read_fs(fs_node_t *node, uint32_t offset, uint32_t size, uint8_t *buffer);
extern void create_task(void (*entry_point)(void), int is_user);
extern fs_node_t* fs_root;

static void sys_exec(const char* path) {
    fs_node_t* node = finddir_fs(fs_root, (char*)path);
    if (!node) {
        // Archivo no encontrado
        return;
    }

    uint8_t* buffer = (uint8_t*)kmalloc(node->length);
    read_fs(node, 0, node->length, buffer);

    create_task((void(*)())buffer, 1);
    // Nota: El buffer no se libera aquí, se convierte en el código de la app.
    // Un sistema más avanzado necesitaría un mejor manejo de la memoria.
}

// El manejador principal de llamadas al sistema.
void syscall_handler(regs_t* r) {
    // El número de la llamada al sistema está en EAX.
    switch (r->eax) {
        case 1: // Syscall 1: print
            sys_print((const char*)r->ebx);
            break;
        case 2: // Syscall 2: exec
            sys_exec((const char*)r->ebx);
            break;
        // ... aquí irían más casos para futuras syscalls ...
        default:
            // Syscall desconocida
            break;
    }
}

// Inicializa el sistema de llamadas al sistema.
void syscalls_init() {
    // 0x80 es la interrupción estándar para syscalls en Linux.
    // 0xEE = Presente, Nivel de Privilegio 3 (usuario), Trampa de 32 bits.
    idt_set_gate(0x80, (uint32_t)syscall_interrupt_handler, 0x08, 0xEE);
}