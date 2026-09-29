#include <stdio.h>

int sum(int *p, int n) {
    int s = 0;

    for (int i = 0; i < n; i++) {
        s += *p;
        p++;
    }

    return s;
}

int main() {
    int arr[] = {10, 20, 30};

    printf("Сумма = %d\n", sum(arr, 3));

    return 0;
}
