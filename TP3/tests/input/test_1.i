float potencia(float base, long exp) {
    float acumulador = 1.0;
    for (; exp > 0; exp--) {
        acumulador *= base;
    }
    return acumulador;
}

j = a;

void rutina(int x);

int main(void) {
    unsigned int i, j = 0xA, a = 06;
    if (a > 5 && j == 10) {
        int b = a;
        while (b != 0) {
            printf("El valor de b es %d\n", b);
            b--;
            ++j;
            continue;
        }
    }

    switch(potencia(j, 2)) {
        case 2:
            break;
        case 4:
            e @double = 0;
            return b-j;
        default:
            return 1+j+b;
    }

    rutina(5);
    return 0;
}

void rutina(int x) {
    do {
        printf("El valor de x es %d \n", x);
        x+=1;
    } while (x < 5);

    if (x == 5 || x > 10) {
        printf("x es 5 o mayor que 10 \n");
    } else {
        printf("x tiene un valor entre 6 y 9 inclusive \n");
    }
}