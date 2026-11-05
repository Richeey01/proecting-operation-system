#define _POSIX_C_SOURCE 200809L

#include "allocator.h"

#include <sys/wait.h>
#include <unistd.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>

#define SMALL_COUNT 5000
#define SMALL_SIZE 32

#define ALT_COUNT 3000
#define ALT_SIZE 64

#define LARGE_COUNT 20
#define LARGE_SIZE (32 * 1024)

typedef void *(*alloc_func)(size_t);
typedef void (*free_func)(void *);

static double current_time(void)
{
    struct timespec ts;

    clock_gettime(CLOCK_MONOTONIC, &ts);

    return (double)ts.tv_sec +
           (double)ts.tv_nsec / 1000000000.0;
}

static long peak_rss_kb(void)
{
    struct rusage usage;

    getrusage(RUSAGE_SELF, &usage);

    return usage.ru_maxrss;
}

static double custom_fragmentation(void)
{
    size_t total_free = allocator_free_memory();

    if (total_free == 0) {
        return 0.0;
    }

    size_t largest = allocator_largest_free_block();

    return 1.0 -
           (double)largest / (double)total_free;
}

static void scenario_small(
    const char *name,
    alloc_func allocate,
    free_func release,
    int custom)
{
    void *blocks[SMALL_COUNT] = {NULL};

    double start = current_time();

    for (size_t i = 0; i < SMALL_COUNT; i++) {
        blocks[i] = allocate(SMALL_SIZE);

        if (blocks[i] != NULL) {
            memset(blocks[i], 0, SMALL_SIZE);
        }
    }

    double fragmentation =
        custom ? custom_fragmentation() : -1.0;

    for (size_t i = 0; i < SMALL_COUNT; i++) {
        release(blocks[i]);
    }

    double end = current_time();

    printf(
        "%-12s | small       | %10.6f s | %8ld KB | ",
        name,
        end - start,
        peak_rss_kb()
    );

    if (custom) {
        printf("%.4f\n", fragmentation);
    } else {
        printf("N/A\n");
    }
}

static void scenario_alternating(
    const char *name,
    alloc_func allocate,
    free_func release,
    int custom)
{
    void *blocks[ALT_COUNT] = {NULL};

    double start = current_time();

    for (size_t i = 0; i < ALT_COUNT; i++) {
        blocks[i] = allocate(ALT_SIZE);

        if (blocks[i] != NULL) {
            memset(blocks[i], 0, ALT_SIZE);
        }
    }

    for (size_t i = 0; i < ALT_COUNT; i += 2) {
        release(blocks[i]);
        blocks[i] = NULL;
    }

    double fragmentation =
        custom ? custom_fragmentation() : -1.0;

    for (size_t i = 0; i < ALT_COUNT; i += 2) {
        blocks[i] = allocate(ALT_SIZE);
    }

    for (size_t i = 0; i < ALT_COUNT; i++) {
        release(blocks[i]);
    }

    double end = current_time();

    printf(
        "%-12s | alternating | %10.6f s | %8ld KB | ",
        name,
        end - start,
        peak_rss_kb()
    );

    if (custom) {
        printf("%.4f\n", fragmentation);
    } else {
        printf("N/A\n");
    }
}

static void scenario_large(
    const char *name,
    alloc_func allocate,
    free_func release,
    int custom)
{
    void *blocks[LARGE_COUNT] = {NULL};

    double start = current_time();

    for (size_t i = 0; i < LARGE_COUNT; i++) {
        blocks[i] = allocate(LARGE_SIZE);

        if (blocks[i] != NULL) {
            memset(blocks[i], 0, LARGE_SIZE);
        }
    }

    double fragmentation =
        custom ? custom_fragmentation() : -1.0;

    for (size_t i = 0; i < LARGE_COUNT; i++) {
        release(blocks[i]);
    }

    double end = current_time();

    printf(
        "%-12s | large       | %10.6f s | %8ld KB | ",
        name,
        end - start,
        peak_rss_kb()
    );

    if (custom) {
        printf("%.4f\n", fragmentation);
    } else {
        printf("N/A\n");
    }
}

static void system_free(void *ptr)
{
    free(ptr);
}

typedef enum {
    SCENARIO_SMALL,
    SCENARIO_ALTERNATING,
    SCENARIO_LARGE
} Scenario;

static void run_one_test(
    const char *name,
    alloc_func allocate,
    free_func release,
    int custom,
    Scenario scenario)
{
    switch (scenario) {
        case SCENARIO_SMALL:
            scenario_small(name, allocate, release, custom);
            break;

        case SCENARIO_ALTERNATING:
            scenario_alternating(name, allocate, release, custom);
            break;

        case SCENARIO_LARGE:
            scenario_large(name, allocate, release, custom);
            break;
    }
}

static void run_in_child(
    const char *name,
    alloc_func allocate,
    free_func release,
    int custom,
    Scenario scenario,
    AllocationStrategy strategy)
{
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        if (custom) {
            set_strategy(strategy);
        }

        run_one_test(
            name,
            allocate,
            release,
            custom,
            scenario
        );

        if (custom) {
            allocator_cleanup();
        }

        fflush(stdout);
        _exit(EXIT_SUCCESS);
    }

    int status = 0;

    if (waitpid(pid, &status, 0) < 0) {
        perror("waitpid");
        exit(EXIT_FAILURE);
    }

    if (!WIFEXITED(status) ||
        WEXITSTATUS(status) != EXIT_SUCCESS) {
        fprintf(stderr, "Ошибка benchmark-процесса\n");
        exit(EXIT_FAILURE);
    }
}

static void run_custom_strategy(
    AllocationStrategy strategy,
    const char *name)
{
    run_in_child(
        name,
        my_malloc,
        my_free,
        1,
        SCENARIO_SMALL,
        strategy
    );

    run_in_child(
        name,
        my_malloc,
        my_free,
        1,
        SCENARIO_ALTERNATING,
        strategy
    );

    run_in_child(
        name,
        my_malloc,
        my_free,
        1,
        SCENARIO_LARGE,
        strategy
    );
}

static void run_glibc(void)
{
    run_in_child(
        "glibc malloc",
        malloc,
        system_free,
        0,
        SCENARIO_SMALL,
        FIRST_FIT
    );

    run_in_child(
        "glibc malloc",
        malloc,
        system_free,
        0,
        SCENARIO_ALTERNATING,
        FIRST_FIT
    );

    run_in_child(
        "glibc malloc",
        malloc,
        system_free,
        0,
        SCENARIO_LARGE,
        FIRST_FIT
    );
}

int main(void)
{
    printf(
        "Allocator    | Scenario     | Time         | Peak RSS    | Fragmentation\n"
    );

    printf(
        "-------------+--------------+--------------+-------------+--------------\n"
    );

    fflush(stdout);

    run_custom_strategy(FIRST_FIT, "First Fit");
    run_custom_strategy(BEST_FIT, "Best Fit");
    run_glibc();

    return 0;
}
