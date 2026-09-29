#include <stdio.h>

void print_value(int *ptr) {
    printf("Value: %d\n", *ptr);
}

int main() {
    int *p = NULL;
    print_value(p);
    return 0;
}
