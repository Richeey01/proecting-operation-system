#include <stdio.h>

void reverse(int *arr, int size) {
    int *s = arr;
    int *e = arr + size - 1;
    while (s < e) {
        int tmp = *s;
        *s++ = *e;
        *e-- = tmp;
    }
}

void print_array(int *arr, int size) {
    for (int i = 0; i < size; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int main(void) {
    int a[] = {1, 2, 3, 4, 5, 6};
    reverse(a, 6);
    print_array(a, 6);

    int b[] = {10, 20, 30, 40, 50};
    reverse(b, 5);
    print_array(b, 5);

    return 0;
}
