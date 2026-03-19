# Configuración de Pre-commit — SSL UTN FRBA

Este repositorio incluye **hooks de pre-commit**: herramientas que se ejecutan
automáticamente cada vez que hacés `git commit`, *antes* de que el commit se
registre. Si alguno detecta un problema, el commit se cancela y podés ver qué
hay que corregir.

Es la misma idea que un CI/CD (como los Actions de GitHub), pero en tu máquina
y de forma inmediata, sin necesidad de hacer push.

---

## ¿Qué hace cada hook?

| Hook | Qué hace | ¿Bloquea el commit? |
|---|---|---|
| `check-added-large-files` | Avisa si intentás commitear un binario o archivo pesado (>500 KB) | Sí |
| `check-yaml` | Valida la sintaxis de archivos `.yml` / `.yaml` | Sí |
| `end-of-file-fixer` | Se asegura de que todos los archivos terminen con una línea en blanco | Sí (corrige automático) |
| `trailing-whitespace` | Elimina los espacios en blanco al final de cada línea | Sí (corrige automático) |
| `clang-format` | Formatea el código C automáticamente según el estilo Google | Sí (corrige automático) |
| `cppcheck` | Análisis estático: detecta posibles bugs y problemas de estilo en C | No (solo informa) |
| `cpplint` | Verifica que el código siga las convenciones del Google C++ Style Guide | No (solo informa) |

> Los hooks que dicen "corrige automático" modifican los archivos por vos.
> Después de que corran, revisá los cambios con `git diff`, hacé `git add` de
> nuevo y reintentá el commit.

---

## Estilo de código: Google C++ Style Guide

El formato del código está definido en el archivo `.clang-format` (en la raíz
del repo) y sigue el **Google C++ Style Guide** adaptado para C. Las
características principales son:

- Indentación de **2 espacios** (sin tabs)
- Llave de apertura `{` en la **misma línea** que la sentencia
- Longitud máxima de línea: **80 caracteres**
- Punteros pegados al tipo: `int* p` (no `int *p`)

Ejemplo de código bien formateado:

```c
int calcular_maximo(int a, int b) {
  if (a > b) {
    return a;
  }
  return b;
}
```

No es necesario memorizar estas reglas: `clang-format` las aplica
automáticamente en cada commit. Lo importante es entender *por qué* existe un
estilo único: facilita la lectura del código ajeno y reduce el ruido en los
diffs de los Pull Requests.

---

## Instalación

### 1. Instalar dependencias del sistema

**macOS:**
```bash
brew install pre-commit clang-format cppcheck
pip install cpplint
```

**Ubuntu / Debian:**
```bash
sudo apt-get install -y clang-format cppcheck python3-pip
pip install pre-commit cpplint
```

**Windows (WSL recomendado):**
Seguí los pasos de Ubuntu dentro de WSL.

### 2. Activar los hooks en tu clon del repositorio

Esto solo hay que hacerlo **una vez por repositorio clonado**:

```bash
pre-commit install
```

Deberías ver:
```
pre-commit installed at .git/hooks/pre-commit
```

A partir de ahí, cada `git commit` ejecutará los hooks automáticamente.

### 3. Verificar que todo funciona

Podés correr los hooks manualmente sobre todos los archivos sin hacer un commit:

```bash
pre-commit run --all-files
```

---

## Flujo típico de trabajo

```
git add mis_cambios.c
git commit -m "feat: implementar autómata"

# Si clang-format reformateó algo:
# → "clang-format (formato automático)....Failed"
# → El commit NO se realizó

git diff                     # revisá qué cambió
git add mis_cambios.c        # volvé a agregar con el formato corregido
git commit -m "feat: implementar autómata"   # ahora sí pasa
```

---

## Preguntas frecuentes

**¿Por qué mi commit fue rechazado si el código "funciona"?**
Los hooks no verifican si el código compila o funciona, sino que el formato y
el estilo sean consistentes. Un código bien formateado es más fácil de leer y
revisar por tus compañeros y docentes.

**¿Puedo saltear los hooks en un caso urgente?**
Sí, con `git commit --no-verify`. Pero usalo solo en situaciones excepcionales:
el CI de GitHub va a correr los mismos chequeos de todas formas.

**`cppcheck` o `cpplint` muestran advertencias pero el commit pasó, ¿es un error?**
No. Esos dos hooks son **informativos**: te muestran sugerencias pero no
cancelan el commit. Leé las advertencias y evaluá si aplican a tu código.

**¿Qué hago si `clang-format` reformateó algo que no quiero cambiar?**
Revisá el diff con `git diff`. Si el cambio tiene sentido (generalmente lo
tiene), hacé `git add` y reintentá. Si necesitás preservar un bloque sin
formatear (por ejemplo, una tabla ASCII o código generado), podés marcarlo:
```c
// clang-format off
int tabla[3][3] = {{1,0,0},{0,1,0},{0,0,1}};
// clang-format on
```
