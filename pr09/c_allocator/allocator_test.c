
#include "allocator.h"

#include <stdio.h>
#include <string.h>

static void test_strategy(AllocationStrategy strategy, const char *name)
{
    printf("\n=== %s ===\n", name);

    set_strategy(strategy);

    char *first = my_malloc(100);
    char *second = my_malloc(200);
    char *third = my_malloc(300);

    if (first == NULL || second == NULL || third == NULL) {
        printf("Ошибка выделения памяти\n");
        return;
    }

    strcpy(first, "Hello allocator");
    strcpy(second, "Memory management");

    printf("Первый блок: %s\n", first);
    printf("Второй блок: %s\n", second);

    printf("Занято: %zu байт\n", allocator_used_memory());
    printf("Свободно: %zu байт\n", allocator_free_memory());

    my_free(second);

    printf("После освобождения второго блока:\n");
    printf("Занято: %zu байт\n", allocator_used_memory());
    printf("Свободно: %zu байт\n", allocator_free_memory());

    char *resized = my_realloc(first, 250);

    if (resized != NULL) {
        printf("После realloc: %s\n", resized);
        my_free(resized);
    } else {
        printf("Ошибка realloc\n");
        my_free(first);
    }

    my_free(third);

    printf("После освобождения всех блоков:\n");
    printf("Занято: %zu байт\n", allocator_used_memory());
    printf("Свободно: %zu байт\n", allocator_free_memory());
}

int main(void)
{
    printf("Общий размер региона: %zu байт\n",
           allocator_total_memory());

    test_strategy(FIRST_FIT, "First Fit");
    allocator_cleanup();

    test_strategy(BEST_FIT, "Best Fit");
    allocator_cleanup();

    return 0;
}
