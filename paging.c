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
    page_table_t* pdpt = (page_table_t*)(kernel_pml4->entries[pml4_index].frame << 12);
    if (!pdpt) {
        pdpt = (page_table_t*)alloc_frame();
        kernel_pml4->entries[pml4_index].frame = (uint64_t)pdpt >> 12;
        kernel_pml4->entries[pml4_index].present = 1;
        kernel_pml4->entries[pml4_index].rw = 1;
    }

    // Obtener el PD del PDPT
    page_table_t* pd = (page_table_t*)(pdpt->entries[pdpt_index].frame << 12);
    if (!pd) {
        pd = (page_table_t*)alloc_frame();
        pdpt->entries[pdpt_index].frame = (uint64_t)pd >> 12;
        pdpt->entries[pdpt_index].present = 1;
        pdpt->entries[pdpt_index].rw = 1;
    }

    // Obtener la PT del PD
    page_table_t* pt = (page_table_t*)(pd->entries[pd_index].frame << 12);
    if (!pt) {
        pt = (page_table_t*)alloc_frame();
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
    // Limpiar la tabla
    for(int i=0; i<TABLE_ENTRIES; i++) kernel_pml4->entries[i].present = 0;

    // Mapear los primeros 2MB de memoria (donde está el kernel)
    for (uint64_t i = 0; i < 0x200000; i += FRAME_SIZE) {
        map_page(i, i, PAGE_WRITE);
    }

    // Cargar el nuevo mapa de memoria.
    load_pml4(kernel_pml4);
}