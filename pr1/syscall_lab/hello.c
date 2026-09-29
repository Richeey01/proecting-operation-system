#include <stdio.h>

int main() {
    float fahr, celsius;
    int lower, upper, step;

    lower = 0;
    upper = 300;
    step = 20;

    fahr = lower;
    printf("Fahr\tCelsius\n");
    while (fahr <= upper) {
        celsius = (5.0 / 9.0) * (fahr - 32.0);
        printf("%6.1f\t%6.1f\n", fahr, celsius);
        fahr = fahr + step;
    }

    printf("End of table\n");
    return 0;
}
