# Rúbrica de Evaluación — TP4: Analizador léxico, sintáctico y semántico (Integrador)

## Contexto

Extender el TP3 con **análisis semántico completo**: Tabla de Símbolos (TS), control de tipos,
validación de declaraciones/definiciones, invocaciones a funciones, asignaciones y sentencias
`return`. El reporte tiene 5 secciones (variables, funciones, errores semánticos, sintácticos,
léxicos). **Este es el TP integrador con defensa oral obligatoria.**

---

## Criterios de evaluación

### 1. Tabla de Símbolos (TS) implementada con memoria dinámica [OBLIGATORIO — crítico]
- DEBE existir una implementación de TS con memoria dinámica (lista enlazada, hash, árbol, etc.).
- La TS debe almacenar al menos: identificador, tipo de dato, categoría (variable/función), ubicación (línea, columna).
- Para funciones: parámetros (tipo y nombre) y tipo de retorno.
- Toda la memoria de la TS debe liberarse al final.

### 2. Validación semántica: Control de tipos en multiplicación [OBLIGATORIO]
- Verificar tipos en la operación binaria `*` cuando algún operando es un identificador.
- Error esperado: `L:C: Operandos invalidos del operador binario * (tienen 'TIPO_L' y 'TIPO_R')`.

### 3. Validación semántica: Control de declaración de símbolos [OBLIGATORIO — crítico]
Implementar todos estos casos:
- Identificador usado sin declarar: `L:C: 'ID' sin declarar`.
- Redeclaración con tipo diferente de símbolo (variable ↔ función): `L:C: 'ID' redeclarado como un tipo diferente de simbolo`.
- Conflicto de tipos (mismo tipo de símbolo, tipos de dato distintos): `L:C: conflicto de tipos para 'ID'; la ultima es de tipo 'TIPO_A'`.
- Redeclaración de variable (mismos tipos): `L:C: Redeclaracion de 'ID'`.
- Redefinición de función (mismos tipos): `L:C: Redefinicion de 'ID'`.
- Nota: funciones pueden tener múltiples prototipos (declaraciones) sin error, siempre que los tipos coincidan.

### 4. Validación semántica: Invocación a funciones [OBLIGATORIO]
- Función no declarada: `L:C: Funcion 'ID' sin declarar`.
- Invocar un objeto que no es función: `L:C: El objeto invocado 'ID' no es una funcion o un puntero a una funcion`.
- Menos argumentos que parámetros: `L:C: Insuficientes argumentos para la funcion 'ID'`.
- Más argumentos que parámetros: `L:C: Demasiados argumentos para la funcion 'ID'`.
- Tipo incompatible de argumento: `L:C: Incompatibilidad de tipos para el argumento # de 'ID'`.
- Uso del valor de retorno de función `void`: `L:C: No se ignora el valor de retorno void como deberia ser`.

### 5. Validación semántica: Asignación [OBLIGATORIO]
- Inicialización con tipo incompatible: `L:C: Incompatibilidad de tipos al inicializar el tipo 'TIPO_L' usando el tipo 'TIPO_R'`.
- Asignación a variable `const`: `L:C: Asignacion de la variable de solo lectura 'ID'`.
- Sin valor-L modificable: `L:C: Se requiere un valor-L modificable como operando izquierdo de la asignacion`.

### 6. Validación semántica: Sentencias return [OBLIGATORIO]
- `return` sin valor en función no-void: `L:C: 'return' sin valor en una funcion que no retorna void`.
- Tipo de retorno incompatible: `L:C: Incompatibilidad de tipos al retornar el tipo 'TIPO_R' pero se esperaba 'TIPO_D'`.

### 7. Formato exacto de mensajes de error semántico [OBLIGATORIO]
- Los mensajes DEBEN seguir exactamente el formato del enunciado (ver arriba).
- Los `Nota:` asociados deben aparecer en la línea siguiente.
- Los errores deben listarse en orden de aparición.

### 8. Las 5 secciones del reporte en orden correcto [OBLIGATORIO]
1. Variables declaradas: tipo de dato + número de línea y columna (usando TS), por orden de aparición.
2. Funciones declaradas/definidas: mismo formato que TP3 (usando TS).
3. Errores semánticos: por orden de aparición, con línea y columna.
4. Errores sintácticos: estructuras no derivables con línea.
5. Errores léxicos: cadenas no reconocidas con línea y columna.
- Cuando una sección no tiene elementos: `"-"`.

### 9. Todo lo del TP3 [OBLIGATORIO]
- Flex + Bison, gramática completa, estructuras sintácticas mínimas.
- Tracking de ubicaciones con `yylloc` y `%locations`.
- Recovery de errores léxicos y sintácticos.
- Memoria dinámica para el reporte.
- Debug en `stderr`.

### 10. Uso de la TS en el reporte [OBLIGATORIO]
- Las secciones 1 y 2 del reporte deben construirse usando datos de la TS, no listas paralelas.

### 11. Portabilidad [OBLIGATORIO]
- Solo headers estándar de C. Sin POSIX headers.

### 12. Calidad de la implementación de la TS [Buenas prácticas]
- Estructura de datos apropiada para la escala del problema.
- Búsqueda eficiente por identificador.
- Manejo correcto del scope si se implementó.

### 13. README.md completo
- Nombres completos y padrón de todos los integrantes.
- Versiones de Flex y Bison.
- Descripción breve de la estructura de datos de la TS implementada.
- Instrucciones de compilación y ejecución.
