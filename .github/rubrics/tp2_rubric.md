# Rúbrica de Evaluación — TP2: Flex para reconocimiento de categorías léxicas de C

## Contexto

Implementar en C un analizador léxico usando **Flex** que reconozca todas las categorías
léxicas de ANSI C (C89/C90) desde un archivo `.i` preprocesado y genere un **reporte
estructurado con 6 secciones** por stdout.

---

## Criterios de evaluación

### 1. Uso de Flex para el scanner [OBLIGATORIO — crítico]
- DEBE existir al menos un archivo `.l` con la especificación Flex.
- No se acepta un scanner escrito a mano sin Flex.
- Las reglas Flex deben cubrir las categorías léxicas requeridas.
- Los archivos generados por Flex (`.lex.yy.c`) NO deben estar en la entrega.

### 2. Uso obligatorio de memoria dinámica para el reporte [OBLIGATORIO — crítico]
- El enunciado **explícitamente requiere** memoria dinámica para almacenar los datos del reporte.
- **Prohibido**: arreglos estáticos de tamaño fijo para las listas del reporte (identificadores, constantes, etc.).
- Verificar uso de `malloc`, `realloc`, `calloc` para las estructuras de datos.
- Verificar liberación correcta de memoria (`free`) — sin leaks.

### 3. Tracking de línea y columna [OBLIGATORIO]
- Se debe mantener un contador de línea y columna durante el análisis léxico.
- Cada token debe tener posición (línea, columna) accesible.
- El reporte de palabras reservadas y cadenas no reconocidas DEBE incluir estas posiciones.

### 4. Recuperación de error léxico [OBLIGATORIO]
- Ante un token no reconocido, el scanner **no debe detenerse** inmediatamente.
- Debe capturar la cadena no reconocida completa hasta el siguiente espacio, tab o `\n`.
- La cadena completa (no carácter a carácter) debe registrarse como no reconocida.
- Ejemplos de cadenas no reconocidas: `ñandu`, `@double@`, `0xXFF`, `123asd`.

### 5. Debug separado en stderr [Buenas prácticas]
- Los mensajes de debug DEBEN ir a `stderr`, nunca a `stdout`.
- `stdout` solo debe contener el reporte esperado (para que los tests automáticos pasen).
- El debug debe poder habilitarse/deshabilitarse con `#define DEBUG` o variable equivalente.

### 6. Las 6 secciones del reporte en orden correcto [OBLIGATORIO]
1. Listado de identificadores (ordenado alfabéticamente, con conteo de apariciones).
2. Listado de literales cadena (ordenados por longitud ascendente; empate: orden de aparición).
3. Listado de palabras reservadas por categoría sintáctica (con línea y columna de cada aparición).
4. Listado de constantes por tipo:
   - Decimales: valor y total acumulado.
   - Hexadecimales: valor entero decimal equivalente.
   - Octales: valor entero decimal equivalente.
   - Reales: parte entera y mantisa.
   - Caracter: enumeradas por orden de aparición.
5. Listado de operadores/puntuación (con conteo, ordenado por primera aparición).
6. Listado de cadenas no reconocidas (con línea y columna).
- Cuando una sección no tiene elementos, imprimir `"-"`.

### 7. Categorías léxicas correctamente reconocidas [OBLIGATORIO]
- **Constantes enteras**: decimales, octales, hexadecimales con y sin sufijo (`u`, `l`, `ul`, etc.).
- **Constantes reales**: con y sin sufijo (`f`, `l`).
- **Constantes caracter**: simples (`'a'`), con escape simple (`'\n'`), octal (`'\07'`), hexadecimal (`'\xF'`).
- **Literales cadena**: `"texto"`.
- **Palabras reservadas** correctamente categorizadas:
  - Clase almacenamiento: `auto`, `register`, `static`, `extern`, `typedef`.
  - Especificadores tipo: `void`, `char`, `short`, `int`, `long`, `float`, `double`, `signed`, `unsigned`.
  - Calificadores tipo: `const`, `volatile`.
  - Struct/Union: `struct`, `union`.
  - Enumeración: `enum`.
  - Etiqueta: `case`, `default`.
  - Selección: `if`, `else`, `switch`.
  - Iteración: `do`, `while`, `for`.
  - Salto: `goto`, `continue`, `break`, `return`.
  - Unario: `sizeof`.
- **Identificadores** vs palabras reservadas correctamente diferenciados.

### 8. Condiciones de arranque Flex [Buenas prácticas]
- Uso apropiado de condiciones inclusivas (`%s`) o exclusivas (`%x`) para manejar contextos complejos como strings y secuencias de escape.
- Variables globales de Flex aprovechadas: `yyin`, `yyout`, `yyleng`, etc.

### 9. Portabilidad — solo librerías estándar de C [OBLIGATORIO]
- Headers permitidos: `stdio.h`, `stdlib.h`, `string.h`, `math.h`, `errno.h`, `limits.h`.
- Funciones recomendadas: `atoi`, `atof`, `strtoul`, `strtof`, `strtod`, `modf`, `modff`, `strlen`, `strcmp`.
- **Prohibido**: headers POSIX o específicos de SO.

### 10. Nombrado, modularidad y buenas prácticas [Buenas prácticas]
- Código bien estructurado en funciones con responsabilidad única.
- Identificadores descriptivos.
- Sin código duplicado innecesario.

### 11. README.md completo
- Nombres completos y padrón de todos los integrantes.
- Versión de Flex utilizada.
- Instrucciones de compilación y ejecución.
