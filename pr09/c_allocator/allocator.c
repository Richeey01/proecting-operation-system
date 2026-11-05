
#define _DEFAULT_SOURCE

#include "allocator.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define REGION_SIZE (1024 * 1024)

static void *memory_region = NULL;
static size_t region_size = 0;
static Block *first_block = NULL;
static AllocationStrategy current_strategy = FIRST_FIT;

static size_t align_size(size_t size)
{
    const size_t alignment = sizeof(max_align_t);

    if (size > SIZE_MAX - (alignment - 1)) {
        return 0;
    }

    return (size + alignment - 1) / alignment * alignment;
}

static int initialize_allocator(void)
{
    if (memory_region != NULL) {
        return 1;
    }

    long page_size = sysconf(_SC_PAGESIZE);

    if (page_size <= 0) {
        return 0;
    }

    size_t total_size = REGION_SIZE;

    if (total_size < (size_t)page_size) {
        total_size = (size_t)page_size;
    }

    memory_region = mmap(
        NULL,
        total_size,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    if (memory_region == MAP_FAILED) {
        memory_region = NULL;
        return 0;
    }

    region_size = total_size;
    first_block = (Block *)memory_region;

    first_block->size = region_size - sizeof(Block);
    first_block->is_free = true;
    first_block->next = NULL;

    return 1;
}

static Block *find_block(size_t size)
{
    Block *current = first_block;
    Block *best = NULL;

    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            if (current_strategy == FIRST_FIT) {
                return current;
            }

            if (best == NULL || current->size < best->size) {
                best = current;
            }
        }

        current = current->next;
    }

    return best;
}

static void split_block(Block *block, size_t size)
{
    if (block->size < size) {
        return;
    }

    if (block->size - size <
        sizeof(Block) + sizeof(max_align_t)) {
        return;
    }

    char *new_address = (char *)(block + 1) + size;
    Block *new_block = (Block *)new_address;

    new_block->size = block->size - size - sizeof(Block);
    new_block->is_free = true;
    new_block->next = block->next;

    block->size = size;
    block->next = new_block;
}

static void merge_blocks(void)
{
    Block *current = first_block;

    while (current != NULL && current->next != NULL) {
        Block *next = current->next;

        if (current->is_free && next->is_free) {
            current->size += sizeof(Block) + next->size;
            current->next = next->next;
        } else {
            current = current->next;
        }
    }
}

void set_strategy(AllocationStrategy strategy)
{
    if (strategy == FIRST_FIT || strategy == BEST_FIT) {
        current_strategy = strategy;
    }
}

void *my_malloc(size_t size)
{
    if (size == 0) {
        return NULL;
    }

    size_t aligned_size = align_size(size);

    if (aligned_size == 0 || !initialize_allocator()) {
        return NULL;
    }

    Block *block = find_block(aligned_size);

    if (block == NULL) {
        return NULL;
    }

    split_block(block, aligned_size);
    block->is_free = false;

    return (void *)(block + 1);
}

void my_free(void *ptr)
{
    if (ptr == NULL || memory_region == NULL) {
        return;
    }

    uintptr_t address = (uintptr_t)ptr;
    uintptr_t start = (uintptr_t)memory_region;
    uintptr_t end = start + region_size;

    if (address <= start || address >= end) {
        return;
    }

    Block *current = first_block;

    while (current != NULL) {
        if ((void *)(current + 1) == ptr) {
            if (current->is_free) {
                return;
            }

            current->is_free = true;
            merge_blocks();
            return;
        }

        current = current->next;
    }
}

void *my_realloc(void *ptr, size_t new_size)
{
    if (ptr == NULL) {
        return my_malloc(new_size);
    }

    if (new_size == 0) {
        my_free(ptr);
        return NULL;
    }

    size_t aligned_size = align_size(new_size);

    if (aligned_size == 0) {
        return NULL;
    }

    Block *current = first_block;

    while (current != NULL) {
        if ((void *)(current + 1) == ptr) {
            if (current->is_free) {
                return NULL;
            }

            if (current->size >= aligned_size) {
                split_block(current, aligned_size);
                return ptr;
            }

            void *new_ptr = my_malloc(new_size);

            if (new_ptr == NULL) {
                return NULL;
            }

            memcpy(new_ptr, ptr, current->size);
            current->is_free = true;
            merge_blocks();

            return new_ptr;
        }

        current = current->next;
    }

    return NULL;
}

size_t allocator_used_memory(void)
{
    size_t total = 0;
    Block *current = first_block;

    while (current != NULL) {
        if (!current->is_free) {
            total += current->size;
        }

        current = current->next;
    }

    return total;
}

size_t allocator_free_memory(void)
{
    size_t total = 0;
    Block *current = first_block;

    while (current != NULL) {
        if (current->is_free) {
            total += current->size;
        }

        current = current->next;
    }

    return total;
}

size_t allocator_total_memory(void)
{
    if (!initialize_allocator()) {
        return 0;
    }

    return region_size - sizeof(Block);
}

size_t allocator_largest_free_block(void)
{
    size_t largest = 0;
    Block *current = first_block;

    while (current != NULL) {
        if (current->is_free && current->size > largest) {
            largest = current->size;
        }

        current = current->next;
    }

    return largest;
}

void allocator_cleanup(void)
{
    if (memory_region != NULL) {
        munmap(memory_region, region_size);

        memory_region = NULL;
        region_size = 0;
        first_block = NULL;
    }
}
