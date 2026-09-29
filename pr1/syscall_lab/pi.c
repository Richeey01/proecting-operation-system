#include <stdio.h>

int main() {
    const double PI = 3.14159;
    double r, S;

    printf("Введите радиус круга: ");
    scanf("%lf", &r);

    S = PI * r * r;

    printf("Площадь круга: %.2f\n", S);

    return 0;
}
