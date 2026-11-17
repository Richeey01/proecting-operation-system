#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#define ARRAY_SIZE (64 * 1024 * 1024)
#define REPEATS 20

static double now_seconds(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    return ts.tv_sec + ts.tv_nsec / 1e9;
}

static void test(char *array, size_t stride) {
    volatile unsigned long long sum = 0;

    double start = now_seconds();

    for (int r = 0; r < REPEATS; r++) {
        for (size_t i = 0; i < ARRAY_SIZE; i += stride) {
            sum += (unsigned char)array[i];
        }
    }

    double elapsed = now_seconds() - start;

    size_t accesses =
        ((ARRAY_SIZE + stride - 1) / stride) * REPEATS;

    printf(
        "Шаг: %5zu байт | "
        "Время: %.6f сек | "
        "нс/доступ: %.2f | сумма: %llu\n",
        stride,
        elapsed,
        elapsed * 1e9 / accesses,
        sum
    );
}

int main(int argc, char **argv) {
    char *array = mmap(
        NULL,
        ARRAY_SIZE,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    if (array == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    if (argc > 1 && argv[1][0] == 'h') {
        if (madvise(array, ARRAY_SIZE, MADV_HUGEPAGE) != 0) {
            perror("madvise");
        }
        puts("Режим: MADV_HUGEPAGE");
    } else {
        if (madvise(array, ARRAY_SIZE, MADV_NOHUGEPAGE) != 0) {
            perror("madvise");
        }
        puts("Режим: MADV_NOHUGEPAGE");
    }

    // Выделяем физические страницы заранее
    for (size_t i = 0; i < ARRAY_SIZE; i += 4096) {
        array[i] = 1;
    }

    test(array, 64);
    test(array, 4096);

    munmap(array, ARRAY_SIZE);
    return 0;
}