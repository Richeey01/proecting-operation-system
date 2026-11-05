CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -Wpedantic -Werror

all: allocator_test benchmark

allocator_test: allocator.c allocator_test.c allocator.h
	$(CC) $(CFLAGS) allocator.c allocator_test.c -o allocator_test

benchmark: allocator.c benchmark.c allocator.h
	$(CC) $(CFLAGS) allocator.c benchmark.c -o benchmark

clean:
	rm -f allocator_test benchmark *.o

valgrind: allocator_test
	valgrind --leak-check=full \
		--show-leak-kinds=all \
		--track-origins=yes \
		--error-exitcode=1 \
		./allocator_test
