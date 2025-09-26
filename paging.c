#include "paging.h"
#include "memory.h"
#include <stddef.h> // Para NULL

// El PML4 del kernel
static page_table_t* kernel_pml4 = NULL;

// Función para cargar el nuevo mapa de memoria
extern void load_pml4(page_table_t* pml4);

void map_page(uint64_t virt_addr, uint64_t phys_addr, uint64_t flags) {
    // Extraer los índices de la dirección virtual
    uint64_t pml4_index = (virt_addr >> 39) & 0x1FF;
    uint64_t pdpt_index = (virt_addr >> 30) & 0x1FF;
    uint64_t pd_index = (virt_addr >> 21) & 0x1FF;
    uint64_t pt_index = (virt_addr >> 12) & 0x1FF;

    // Obtener el PDPT de la PML4
    page_table_t* pdpt;
    if (kernel_pml4->entries[pml4_index].present) {
        pdpt = (page_table_t*)(kernel_pml4->entries[pml4_index].frame << 12);
    } else {
        pdpt = (page_table_t*)alloc_frame();
        for(int i=0; i<TABLE_ENTRIES; i++) pdpt->entries[i].present = 0;
        kernel_pml4->entries[pml4_index].frame = (uint64_t)pdpt >> 12;
        kernel_pml4->entries[pml4_index].present = 1;
        kernel_pml4->entries[pml4_index].rw = 1;
    }

    // Obtener el PD del PDPT
    page_table_t* pd;
    if (pdpt->entries[pdpt_index].present) {
        pd = (page_table_t*)(pdpt->entries[pdpt_index].frame << 12);
    } else {
        pd = (page_table_t*)alloc_frame();
        for(int i=0; i<TABLE_ENTRIES; i++) pd->entries[i].present = 0;
        pdpt->entries[pdpt_index].frame = (uint64_t)pd >> 12;
        pdpt->entries[pdpt_index].present = 1;
        pdpt->entries[pdpt_index].rw = 1;
    }

    // Obtener la PT del PD
    page_table_t* pt;
    if (pd->entries[pd_index].present) {
        pt = (page_table_t*)(pd->entries[pd_index].frame << 12);
    } else {
        pt = (page_table_t*)alloc_frame();
        for(int i=0; i<TABLE_ENTRIES; i++) pt->entries[i].present = 0;
        pd->entries[pd_index].frame = (uint64_t)pt >> 12;
        pd->entries[pd_index].present = 1;
        pd->entries[pd_index].rw = 1;
    }

    // Mapear la página en la PT
    pt->entries[pt_index].frame = phys_addr >> 12;
    pt->entries[pt_index].present = 1;
    pt->entries[pt_index].rw = (flags & PAGE_WRITE) ? 1 : 0;
    pt->entries[pt_index].user = (flags & PAGE_USER) ? 1 : 0;
}

void paging_init() {
    // Crear un nuevo PML4 para el kernel
    kernel_pml4 = (page_table_t*)alloc_frame();
    for(int i=0; i<TABLE_ENTRIES; i++) kernel_pml4->entries[i].present = 0;

    // Mapear los primeros 4MB de memoria (suficiente para el kernel y la video ram)
    for (uint64_t i = 0; i < 0x400000; i += FRAME_SIZE) {
        map_page(i, i, PAGE_WRITE);
    }

    // Cargar el nuevo mapa de memoria.
    load_pml4(kernel_pml4);
}