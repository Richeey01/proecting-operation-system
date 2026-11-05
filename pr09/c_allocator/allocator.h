
#ifndef ALLOCATOR_H
#define ALLOCATOR_H

#include <stddef.h>
#include <stdbool.h>

// Стратегии распределения памяти
typedef enum {
    FIRST_FIT,
    BEST_FIT
} AllocationStrategy;

// Метаданные одного блока памяти
typedef struct Block {
    size_t size;
    bool is_free;
    struct Block *next;
    max_align_t alignment;
} Block;

// Выбор стратегии распределения
void set_strategy(AllocationStrategy strategy);

// Выделение памяти
void *my_malloc(size_t size);

// Освобождение памяти
void my_free(void *ptr);

// Изменение размера блока
void *my_realloc(void *ptr, size_t new_size);

// Завершение работы аллокатора
void allocator_cleanup(void);

// Получение размера занятой памяти
size_t allocator_used_memory(void);

// Получение размера свободной памяти
size_t allocator_free_memory(void);

// Получение размера всего региона
size_t allocator_total_memory(void);

// Размер самого большого свободного блока
size_t allocator_largest_free_block(void);

#endif
