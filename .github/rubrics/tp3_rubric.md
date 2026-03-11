# Rúbrica de Evaluación — TP3: Bison para reconocimiento de estructuras sintácticas

## Contexto

Extender el TP2 implementando un **analizador sintáctico usando Bison junto con Flex**
que reconozca las estructuras sintácticas mínimas de ANSI C (C89/C90) y genere un
reporte con 5 secciones.

---

## Criterios de evaluación

### 1. Uso de Bison + Flex [OBLIGATORIO — crítico]
- DEBE existir un archivo `.y` (gramática Bison) y un archivo `.l` (scanner Flex).
- Los archivos generados (`.tab.c`, `.tab.h`, `.lex.yy.c`) NO deben estar en la entrega.
- La integración Flex ↔ Bison debe ser correcta (Flex provee tokens a Bison).

### 2. Estructuras sintácticas mínimas implementadas [OBLIGATORIO — crítico]
Verificar que la gramática cubre al menos:
- **Expresiones**: primarias (identificador, constante, literal cadena, `(expr)`), post-fijas (llamadas a función, `++`/`--` postfijo), unarias (`++`/`--` prefijo), multiplicativas (`*`, `/`), aditivas (`+`, `-`), relacionales (`<`, `>`, `<=`, `>=`), igualdad (`==`, `!=`), lógicas AND (`&&`), lógicas OR (`||`), asignación (`=`, `+=`, `-=`, `*=`, `/=`).
- **Declaraciones**: variables simples (con posible múltiple declaración por línea), prototipos de funciones simples.
- **Sentencias**: expresión, compuestas (`{}`), selección (`if`, `if/else`, `switch`), iteración (`while`, `do/while`, `for`), etiquetadas (`case`, `default`), salto (`continue`, `break`, `return`).
- **Definiciones externas**: definiciones de funciones simples, declaraciones globales.

### 3. Uso obligatorio de memoria dinámica para el reporte [OBLIGATORIO]
- Mismo criterio que TP2: memoria dinámica para almacenar los datos del reporte.
- No arreglos estáticos de tamaño fijo para las listas.
- Liberación correcta de toda memoria alocada.

### 4. Tracking de ubicaciones con yylloc [OBLIGATORIO]
- DEBE usarse la directiva `%locations` en el archivo Bison.
- Las ubicaciones (línea, columna) deben pasarse del scanner al parser via `yylloc`.
- El reporte de sentencias DEBE incluir línea y columna de cada sentencia.

### 5. Manejo de errores léxicos y sintácticos [OBLIGATORIO]
- **Léxico**: recovery hasta el siguiente espacio, tab o `\n` (igual que TP2).
- **Sintáctico**: uso del token `error` de Bison para capturar errores y seguir procesando.
- Recovery sintáctico a partir del siguiente `;` o `\n`.
- Los errores sintácticos deben aparecer en la sección 4 del reporte.

### 6. Las 5 secciones del reporte en orden correcto [OBLIGATORIO]
1. Listado de variables declaradas: tipo de dato + número de línea, por orden de aparición. Múltiples variables en la misma línea: orden izquierda a derecha.
2. Listado de funciones declaradas/definidas: nombre, tipo (declaracion/definicion), parámetros (tipo nombre), tipo de retorno, número de línea.
3. Listado de sentencias: tipo de sentencia, número de línea y columna, por orden de aparición. Tipos: `for`, `while`, `do/while`, `if`, `if/else`, `switch`, `case`, `default`, `break`, `continue`, `return`.
4. Listado de estructuras sintácticas no válidas: la estructura entre comillas y su número de línea.
5. Listado de cadenas no reconocidas léxicamente: cadena, línea y columna.
- Cuando una sección no tiene elementos, imprimir `"-"`.

### 7. Debug separado en stderr [Buenas prácticas]
- Debug a `stderr`, stdout solo para el reporte.
- Depuración habilitada/deshabilitada con variable o `#define`.
- Opcionalmente: uso de flag `-d` de Flex y `-t` de Bison para debug del autómata.

### 8. Correctitud gramatical [Buenas prácticas]
- Revisar si hay conflictos shift/reduce no justificados que puedan alterar la semántica.
- Las producciones deben ser consistentes con la gramática de ANSI C.
- El clásico conflicto `if/else` (dangling else) debe estar correctamente resuelto.

### 9. Portabilidad [OBLIGATORIO]
- Solo headers estándar de C.
- Sin POSIX headers.

### 10. Nombrado, modularidad y organización del código [Buenas prácticas]
- Separación clara entre el scanner (`.l`), la gramática (`.y`) y el código de soporte (`.c`/`.h`).
- Funciones auxiliares bien nombradas y con responsabilidad única.
- Sin duplicación de lógica entre el TP2 y el TP3.

### 11. README.md completo
- Nombres completos y padrón de todos los integrantes.
- Versiones de Flex y Bison utilizadas.
- Instrucciones de compilación y ejecución.
