# Rúbrica de Evaluación — TP1: Autómata Finito Determinístico para Constantes Enteras de C

## Contexto

Implementar en C un programa que reconozca constantes enteras de ANSI C (C89/C90)
y las clasifique en DECIMAL, OCTAL, HEXADECIMAL o NO RECONOCIDA. El programa lee un
archivo de entrada con cadenas separadas por coma (centinela `,`) y **debe implementar
un AFD procesando carácter a carácter**.

---

## Criterios de evaluación

### 1. Tabla de transiciones implementada como matriz 2D [OBLIGATORIO — crítico]
- DEBE existir una variable de tipo arreglo 2D de la forma `tipo_estado tabla[N_ESTADOS][N_COLUMNAS]`.
- La navegación del AFD (qué estado siguiente tomar) DEBE realizarse indexando esa tabla.
- **Incumplimiento**: si la clasificación se resuelve únicamente con `if/else` o `switch` anidados sin consultar la tabla matricial.
- El tamaño de la tabla debe ser coherente con la cantidad de estados y categorías de caracteres definidas.

### 2. Sin números mágicos — uso de enum o #define [OBLIGATORIO]
- Los estados del AFD deben estar nombrados con `enum` o constantes `#define` descriptivos (ej: `Q0`, `DECIMAL`, `ERROR`).
- Las columnas (categorías de caracteres de entrada) deben estar nombradas con `enum` o `#define`.
- **Incumplimiento**: usar literales `0`, `1`, `2`, `3`... directamente para referirse a estados o columnas.

### 3. Procesamiento carácter a carácter con lookup en tabla [OBLIGATORIO]
- Para cada carácter leído, se debe determinar su columna y consultar `tabla[estado_actual][columna]`.
- El estado final tras procesar toda la cadena determina la clasificación.
- **Incumplimiento**: clasificar la cadena completa con `strcmp`, `strstr`, manipulación de strings, o regex-like logic sin AFD.

### 4. Correctitud de los casos de clasificación [OBLIGATORIO]
- HEXADECIMAL: empieza con `0x` o `0X`, seguido de dígitos `[0-9a-fA-F]` (ej: `0xFF`, `0xaBb1`).
- OCTAL: `0` solo, o `0` seguido de dígitos `[0-7]` (ej: `0`, `010`).
- DECIMAL: dígito `[1-9]` seguido de `[0-9]`, o un dígito `[1-9]` solo. **Nota: `0` es OCTAL, no DECIMAL**.
- NO RECONOCIDA: todo lo demás (ej: `0159`, `0Xx`, `127A`, cadenas con letras no-hex).

### 5. Centinela correcto [OBLIGATORIO]
- La coma `,` debe ser el separador de tokens en el archivo de entrada.
- El programa debe leer hasta EOF procesando correctamente el último token después de la última coma.

### 6. Separación en módulos .c y .h [Buenas prácticas]
- Al menos un `.c` (implementación) y un `.h` (declaraciones, tipos, defines).
- El `.h` debe tener include guard (`#ifndef NOMBRE_H` / `#define NOMBRE_H` / `#endif`).
- No definir variables globales en el `.h` (solo declaraciones `extern` o tipos/defines).

### 7. Portabilidad — solo librerías estándar de C [OBLIGATORIO]
- Headers permitidos: `stdio.h`, `stdlib.h`, `string.h`, `ctype.h`, `errno.h`, `math.h`.
- **Prohibido**: headers POSIX (`unistd.h`, `sys/types.h`, `dirent.h`, etc.) o específicos de SO.
- No usar extensiones GNU-específicas del compilador.

### 8. Nombrado y declaratividad [Buenas prácticas]
- Identificadores descriptivos (no `a`, `x`, `tmp` sin contexto).
- Funciones con responsabilidad única y nombre que describe su propósito.
- Constantes o defines con nombres en MAYÚSCULAS convencionales.

### 9. Eficiencia y uso de memoria [Buenas prácticas]
- Evaluar si el uso de memoria dinámica (`malloc`, `realloc`) es justificado o si un buffer de tamaño fijo sería suficiente.
- Si se usa memoria dinámica: verificar que no haya memory leaks (toda memoria alocada debe liberarse).
- Verificar que no haya buffer overflows potenciales.

### 10. Manejo de errores de I/O [Buenas prácticas]
- Verificar el retorno de `fopen` antes de usar el `FILE*`.
- Manejo apropiado de `EOF`.
- Mensajes de error descriptivos (usando `perror` o `fprintf(stderr, ...)`).

### 11. README.md completo
- Nombres completos y número de padrón de todos los integrantes.
- Estándar de C utilizado (C89, C99, C11, etc.) y versión del compilador gcc.
- Diagrama de estados del AFD y/o tabla de transiciones documentados o referenciados.
- Instrucciones de compilación (`make all`) y ejecución.
