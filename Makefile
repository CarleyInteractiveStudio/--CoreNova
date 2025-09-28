# Makefile para CarleyOS (x86_64, GRUB/ISO)

# Herramientas
ASM = nasm
GCC = gcc
LD = ld
GRUB = grub-mkrescue
QEMU = qemu-system-x86_64

# Banderas
ASMFLAGS = -f elf64
GCCFLAGS = -m64 -ffreestanding -O2 -Wall -Wextra -nostdlib -fno-pie -fno-stack-protector
LDFLAGS = -T linker.ld
QEMUFLAGS = -cdrom carleyos.iso -nographic -serial file:serial.log

# Archivos
SOURCES_ASM = boot.s interrupts.s
SOURCES_C = kernel.c idt.c timer.c keyboard.c shell.c pmm.c heap.c serial.c task.c fs.c
OBJECTS_ASM = $(SOURCES_ASM:.s=.o)
OBJECTS_C = $(SOURCES_C:.c=.o)
KERNEL_BIN = carleyos.bin
ISO_FILE = carleyos.iso
INITRD_TAR = initrd.tar

# Reglas
all: $(ISO_FILE)

$(INITRD_TAR): initrd_files/hola.txt initrd_files/info.txt
	tar -cf $(INITRD_TAR) -C initrd_files .

$(KERNEL_BIN): $(OBJECTS_ASM) $(OBJECTS_C)
	$(LD) $(LDFLAGS) -o $(KERNEL_BIN) $(OBJECTS_ASM) $(OBJECTS_C)

%.o: %.s
	$(ASM) $(ASMFLAGS) $< -o $@

%.o: %.c
	$(GCC) $(GCCFLAGS) -c $< -o $@

$(ISO_FILE): $(KERNEL_BIN) $(INITRD_TAR) grub.cfg
	mkdir -p iso/boot/grub
	cp $(KERNEL_BIN) iso/boot/
	cp $(INITRD_TAR) iso/boot/
	cp grub.cfg iso/boot/grub/
	$(GRUB) -o $(ISO_FILE) iso

run: all
	$(QEMU) $(QEMUFLAGS)

clean:
	rm -f $(KERNEL_BIN) $(OBJECTS_ASM) $(OBJECTS_C) $(INITRD_TAR)
	rm -rf iso $(ISO_FILE)

.PHONY: all run clean