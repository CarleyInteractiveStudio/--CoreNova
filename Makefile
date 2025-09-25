# Makefile para CarleyOS

# Herramientas
ASM = nasm
GCC = gcc
LD = ld
QEMU = qemu-system-i386

# Banderas de compilación
# -felf32: Formato de salida ELF de 32 bits.
# -ffreestanding: No asumir que hay una biblioteca estándar.
# -nostdlib: No enlazar con bibliotecas estándar.
# -lgcc: Enlazar con la biblioteca de ayuda de GCC.
ASMFLAGS = -f elf32
GCCFLAGS = -m32 -ffreestanding -O2 -Wall -Wextra
LDFLAGS = -m elf_i386 -T linker.ld
QEMUFLAGS = -kernel carleyos.bin -nographic

# Archivos fuente
SOURCES_ASM = boot.s interrupts.s
SOURCES_C = kernel.c idt.c keyboard.c timer.c memory.c paging.c kheap.c task.c

# Archivos objeto
OBJECTS_ASM = $(SOURCES_ASM:.s=.o)
OBJECTS_C = $(SOURCES_C:.c=.o)

# Nombre del archivo de salida
OUTPUT = carleyos.bin

# Regla por defecto: compila todo
all: $(OUTPUT)

# Regla para crear el binario final de CarleyOS
$(OUTPUT): $(OBJECTS_ASM) $(OBJECTS_C)
	$(LD) $(LDFLAGS) -o $(OUTPUT) $(OBJECTS_ASM) $(OBJECTS_C)

# Regla para compilar los archivos de ensamblador
%.o: %.s
	$(ASM) $(ASMFLAGS) $< -o $@

# Regla para compilar los archivos de C
%.o: %.c
	$(GCC) $(GCCFLAGS) -c $< -o $@

# Regla para ejecutar en QEMU
run: all
	$(QEMU) $(QEMUFLAGS)

# Regla para limpiar los archivos generados
clean:
	rm -f $(OUTPUT) $(OBJECTS_ASM) $(OBJECTS_C)

.PHONY: all run clean