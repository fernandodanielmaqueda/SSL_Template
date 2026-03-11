#!/usr/bin/env python3
"""
LLM Code Review — SSL UTN-FRBA

Recolecta archivos fuente de un TP y estadísticas de colaboración git,
llama a la API de Anthropic y publica un comentario Markdown en el PR.

Uso:
    python llm_review.py <tp_dir> <rubric_file>

Variables de entorno requeridas:
    ANTHROPIC_API_KEY, GITHUB_TOKEN, PR_NUMBER,
    GITHUB_REPOSITORY, BASE_SHA, HEAD_SHA
"""

import os
import sys
import subprocess
import time
import anthropic
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
MODEL = "claude-sonnet-4-6"
MAX_TOKENS_OUTPUT = 4096

# Límites de truncado para evitar prompts excesivamente costosos
MAX_FILE_LINES = 500          # líneas máximas por archivo individual
MAX_TOTAL_SOURCE_CHARS = 100_000  # ~25 K tokens de código fuente total


# ---------------------------------------------------------------------------
# Recolección de archivos fuente
# ---------------------------------------------------------------------------
def collect_source_files(tp_dir: str) -> dict:
    """
    Busca recursivamente en tp_dir archivos .c .h .l .y
    Excluye archivos generados (lex.yy.c, .tab.c/.tab.h) y binarios.
    Trunca archivos grandes para controlar costos.
    """
    extensions = {".c", ".h", ".l", ".y"}
    skip_patterns = {"lex.yy.c", ".tab.c", ".tab.h", "/bin/", "/obj/", "/.git/"}

    files = {}
    for ext in sorted(extensions):
        for f in sorted(Path(tp_dir).rglob(f"*{ext}")):
            path_str = str(f)
            if any(p in path_str for p in skip_patterns):
                continue
            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue

            lines = content.splitlines()
            if len(lines) > MAX_FILE_LINES:
                content = "\n".join(lines[:MAX_FILE_LINES])
                content += f"\n\n// ... [archivo truncado: se muestran {MAX_FILE_LINES} de {len(lines)} líneas]"

            files[str(f)] = content

    # Si el total supera el presupuesto, truncar los archivos más grandes
    total_chars = sum(len(c) for c in files.values())
    if total_chars > MAX_TOTAL_SOURCE_CHARS:
        ratio = MAX_TOTAL_SOURCE_CHARS / total_chars
        for path in list(files.keys()):
            lines = files[path].splitlines()
            keep = max(50, int(len(lines) * ratio))
            if len(lines) > keep:
                files[path] = "\n".join(lines[:keep])
                files[path] += f"\n\n// ... [truncado por límite de presupuesto de tokens]"

    return files


def load_excluded_authors(config_file: str = ".github/config/docentes.txt") -> set:
    """
    Carga la lista de usernames/nombres a excluir del análisis de colaboración.
    Se compara (case-insensitive) contra nombre y email de cada commit.
    """
    path = Path(config_file)
    if not path.exists():
        return set()
    return {
        line.strip().lower()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def is_excluded(name: str, email: str, excluded: set) -> bool:
    name_l, email_l = name.lower(), email.lower()
    return any(ex in name_l or ex in email_l for ex in excluded)


def collect_readme(tp_dir: str) -> str:
    readme = Path(tp_dir) / "README.md"
    if readme.exists():
        return readme.read_text(errors="replace")
    return "*(README.md no encontrado)*"


# ---------------------------------------------------------------------------
# Estadísticas git
# ---------------------------------------------------------------------------
def git(args: list) -> str:
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30
        )
        return r.stdout.strip() or "*(sin datos)*"
    except Exception as e:
        return f"*(error al ejecutar git: {e})*"


def collect_git_stats(base_sha: str, head_sha: str, tp_dir: str,
                      excluded: set) -> dict:
    """
    Recolecta estadísticas git del PR filtrando autores excluidos (docentes).
    Usa formato estructurado para parsear y filtrar antes de enviar al LLM.
    """
    ref = f"{base_sha}..{head_sha}"
    diff_ref = f"{base_sha}...{head_sha}"

    # Obtener todos los commits con datos estructurados para filtrar
    raw_log = git(["log", ref, "--no-merges",
                   "--format=DELIM|%h|%an|%ae|%ai|%s"])

    # Parsear y filtrar por autores excluidos
    student_commits = []
    excluded_count = 0
    for line in raw_log.splitlines():
        if not line.startswith("DELIM|"):
            continue
        parts = line.split("|", 5)
        if len(parts) < 6:
            continue
        _, sha, name, email, date, subject = parts
        if is_excluded(name, email, excluded):
            excluded_count += 1
            continue
        student_commits.append({
            "sha": sha, "name": name, "email": email,
            "date": date[:10], "subject": subject
        })

    # Reconstruir shortlog solo con commits de alumnos
    author_counts = {}
    for c in student_commits:
        author_counts[c["name"]] = author_counts.get(c["name"], 0) + 1
    shortlog = "\n".join(
        f"  {count}\t{name}"
        for name, count in sorted(author_counts.items(), key=lambda x: -x[1])
    ) or "*(sin commits de alumnos)*"

    # Log legible para el LLM
    commit_log = "\n".join(
        f"COMMIT {c['sha']} | {c['name']} | {c['date']} | {c['subject']}"
        for c in student_commits
    ) or "*(sin commits de alumnos)*"

    # Numstat filtrado: reconstruir por autor
    raw_numstat = git(["log", ref, "--no-merges",
                       "--numstat", "--format=>>>AUTHOR:%an|%ae"])
    filtered_numstat = []
    include = False
    for line in raw_numstat.splitlines():
        if line.startswith(">>>AUTHOR:"):
            parts = line[len(">>>AUTHOR:"):].split("|", 1)
            name = parts[0] if parts else ""
            email = parts[1] if len(parts) > 1 else ""
            include = not is_excluded(name, email, excluded)
            if include:
                filtered_numstat.append(f">>> {name}")
        elif include and line.strip():
            filtered_numstat.append(line)

    # Co-authored-by (solo mensajes de commits de alumnos)
    student_shas = [c["sha"] for c in student_commits]
    coauthors = ""
    if student_shas:
        coauthors = git(["log", "--no-walk"] + student_shas + ["--format=%B"])

    return {
        "total_commits":    str(len(student_commits)),
        "excluded_count":   str(excluded_count),
        "shortlog":         shortlog,
        "commit_log":       commit_log,
        "numstat":          "\n".join(filtered_numstat) or "*(sin datos)*",
        "coauthors":        coauthors,
        "diff_stat":        git(["diff", diff_ref, "--stat", "--", tp_dir]),
    }


# ---------------------------------------------------------------------------
# Construcción del prompt
# ---------------------------------------------------------------------------
def build_prompt(tp_dir: str, rubric: str, source_files: dict,
                 readme: str, git_stats: dict) -> str:

    # Sección de archivos fuente
    sources_md = ""
    for path, content in source_files.items():
        ext = Path(path).suffix
        lang = "c" if ext in {".c", ".h"} else "text"
        sources_md += f"\n#### `{path}`\n```{lang}\n{content}\n```\n"
    if not sources_md:
        sources_md = "*(No se encontraron archivos fuente)*"

    # Limitar co-authored raw a 3000 chars para no desperdiciar tokens
    coauthors_trimmed = git_stats["coauthors"][:3000]
    if len(git_stats["coauthors"]) > 3000:
        coauthors_trimmed += "\n*(mensajes truncados)*"

    return f"""Sos un docente universitario de la materia "Sintaxis y Semántica de los Lenguajes" (SSL) de UTN-FRBA.
Tu tarea es revisar la entrega grupal de {tp_dir} y escribir una **devolución para los estudiantes** como comentario en su Pull Request de GitHub.

Tono y estilo de la devolución:
- Hablales directamente a los estudiantes en segunda persona del plural (ustedes / el grupo).
- Empezá reconociendo lo que está bien hecho antes de señalar lo que falta o puede mejorar.
- Usá un lenguaje constructivo: "una oportunidad de mejora sería...", "podrían considerar...", "vale la pena revisar...".
- Evitá un tono fiscalizador o burocrático. El objetivo es que el grupo aprenda, no que se sienta juzgado.
- Sé concreto pero conciso: no hace falta escribir párrafos extensos.
- El cierre debe ser alentador, reconociendo el esfuerzo del grupo.

Jerarquía de criterios en la rúbrica — es FUNDAMENTAL que la decisión global respete esto:
- **[OBLIGATORIO — crítico]**: Son condiciones sine qua non. Si cualquiera de estos no se cumple, la entrega es ❌ Desaprobada, sin excepción. Señalalo claramente pero sin dramatismo.
- **[OBLIGATORIO]**: Requisitos del enunciado. El incumplimiento de varios de estos también lleva a ❌ Desaprobado. Uno solo con desvío menor puede ameritar ⚠️ Requiere revisión docente.
- **[Buenas prácticas]**: Son deseables y enriquecen la entrega, pero **no determinan la aprobación**. Mencionálas como oportunidades de mejora, no como déficits. Una entrega puede estar ✅ Aprobada aunque alguna buena práctica no esté perfectamente implementada.
- **README.md**: Importante pero secundario. Su ausencia o incompletitud no desaprueba por sí sola; sí merece una mención constructiva.

Formato:
- Markdown compatible con GitHub (se renderiza en la interfaz del PR).
- Tablas Markdown (`| col | col |`) para información tabular.
- Encabezados `##`, `###` para estructurar secciones.
- **Negrita**, `código inline` y bloques de código donde corresponda.

---

## RÚBRICA DE EVALUACIÓN

{rubric}

---

## README DEL TRABAJO (carátula / integrantes)

{readme}

---

## ARCHIVOS FUENTE ENTREGADOS

{sources_md}

---

## DATOS GIT DEL PULL REQUEST

**Commits de alumnos analizados:** {git_stats["total_commits"]} (commits de docentes excluidos del análisis: {git_stats["excluded_count"]})

**Commits por integrante:**
```
{git_stats["shortlog"]}
```

**Detalle de commits (hash | autor | fecha | mensaje):**
```
{git_stats["commit_log"]}
```

**Líneas modificadas por commit y autor:**
```
{git_stats["numstat"]}
```

**Diff total en {tp_dir}:**
```
{git_stats["diff_stat"]}
```

**Mensajes completos de commits (para detectar Co-authored-by):**
```
{coauthors_trimmed}
```

---

## INSTRUCCIONES DE SALIDA

Generá el comentario completo de PR siguiendo **exactamente** la estructura y el formato indicados abajo.
Respondé **únicamente** con el contenido Markdown del comentario, sin ningún texto antes ni después.

---

## Revisión — {tp_dir}

> 🤖 Revisión automática con `{MODEL}` | Tests: ✅ Pasaron

[Párrafo de apertura breve y cercano: saludá al grupo, mencioná el TP y destacá algo positivo general de la entrega antes de entrar en detalle. 2-3 oraciones.]

---

### Resultado: [reemplazar con ✅ Aprobado | ❌ Desaprobado | ⚠️ Requiere revisión docente]

[2-3 oraciones explicando la decisión. Si es positivo, resaltá los puntos fuertes. Si hay problemas, mencioná cuáles son los más relevantes sin ser alarmista.]

---

### Evaluación de rúbrica

| # | Criterio | Peso | Estado | Comentario |
|---|---|---|---|---|
| [N] | [nombre del criterio] | [🔴 Crítico / 🟠 Obligatorio / 🟢 Buena práctica] | [✅ / ❌ / ⚠️] | [observación breve y constructiva; si aplica, mencioná archivo:línea] |

*(una fila por cada criterio — cubrí TODOS; el Peso debe reflejar exactamente la etiqueta de la rúbrica)*

---

### Oportunidades de mejora en el código

| Tipo | Archivo | Línea | Observación | Sugerencia |
|---|---|---|---|---|
| [🐛 Bug / ⚡ Performance / 🔧 Mantenibilidad / 📐 Buenas prácticas / 💡 Sugerencia] | [archivo] | [N] | [qué se observa] | [cómo podría mejorarse] |

*(Si el código está bien, escribir una fila indicando "Sin observaciones significativas.")*

---

### Trabajo en equipo

**Participación por integrante:**

| Integrante | Commits | Líneas +/- | Último commit | Participación |
|---|---|---|---|---|
| [nombre] | [N] | [+X / -Y] | [fecha] | [✅ Activa / ⚠️ Baja / ❌ Sin commits] |

**Detalle de commits:**

| SHA | Autor | Mensaje | Tipo |
|---|---|---|---|
| `[sha]` | [autor] | [mensaje] | [✅ Sustancial / ⚠️ Menor / ❓ A revisar] |

*(máximo 20 commits)*

[Párrafo de análisis del equipo: cómo se distribuyó el trabajo, si hubo colaboración pareja, patrones de trabajo (gradual vs. concentrado al final), uso de Co-authored-by, y cualquier observación relevante para el docente. Tono descriptivo, no acusatorio.]

---

[Cierre alentador de 2-3 oraciones: reconocé el esfuerzo del grupo, mencioná lo que pueden llevarse de aprendizaje de esta entrega. Evitá frases genéricas; que se sienta genuino.]

---
*Revisión automática orientativa — la decisión final es del docente.*
"""


# ---------------------------------------------------------------------------
# Llamada a la API con reintentos
# ---------------------------------------------------------------------------
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 60


def call_llm_with_retries(client, prompt: str) -> str:
    """
    Llama a la API de Anthropic con hasta MAX_RETRIES intentos.
    Espera RETRY_DELAY_SECONDS entre intentos en caso de error transitorio
    (rate limit, error de servidor, timeout).
    Lanza la excepción final si todos los intentos fallan.
    """
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"   Intento {attempt}/{MAX_RETRIES}...")
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS_OUTPUT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response
        except anthropic.AuthenticationError as e:
            # API key inválida — no tiene sentido reintentar
            raise RuntimeError(
                "API key de Anthropic inválida o faltante. "
                "Verificá el secret ANTHROPIC_API_KEY en el repositorio."
            ) from e
        except (anthropic.RateLimitError, anthropic.APIStatusError,
                anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                print(f"   ⚠️  Error transitorio ({type(e).__name__}): {e}")
                print(f"   Reintentando en {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print(f"   ❌ Falló en todos los {MAX_RETRIES} intentos.")
    raise RuntimeError(
        f"La API de Anthropic falló tras {MAX_RETRIES} intentos. "
        f"Último error: {last_exc}"
    ) from last_exc


# ---------------------------------------------------------------------------
# Publicación del comentario en el PR
# ---------------------------------------------------------------------------
def post_pr_comment(pr_number: str, repo: str, token: str, body: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    r = requests.post(url, headers=headers, json={"body": body}, timeout=30)
    if r.status_code == 201:
        print(f"✅ Comentario publicado correctamente en PR #{pr_number}")
    else:
        print(f"❌ Error al publicar comentario: HTTP {r.status_code}")
        print(r.text)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("Uso: llm_review.py <tp_dir> <rubric_file>")
        print("Ejemplo: llm_review.py TP1 .github/rubrics/tp1_rubric.md")
        sys.exit(1)

    tp_dir = sys.argv[1]
    rubric_file = sys.argv[2]

    # Validar variables de entorno
    required_env = [
        "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "PR_NUMBER",
        "GITHUB_REPOSITORY", "BASE_SHA", "HEAD_SHA",
    ]
    env = {k: os.environ.get(k, "") for k in required_env}
    missing = [k for k, v in env.items() if not v]
    if missing:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing)}")
        sys.exit(1)

    # Recolectar datos
    print(f"📁 Recolectando archivos de {tp_dir}...")
    source_files = collect_source_files(tp_dir)
    print(f"   {len(source_files)} archivos encontrados: {list(source_files.keys())}")

    total_chars = sum(len(c) for c in source_files.values())
    print(f"   Total de caracteres de código: {total_chars:,}")

    readme = collect_readme(tp_dir)

    print(f"📋 Leyendo rúbrica: {rubric_file}")
    try:
        rubric = Path(rubric_file).read_text(errors="replace")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de rúbrica: {rubric_file}")
        sys.exit(1)

    excluded = load_excluded_authors()
    if excluded:
        print(f"🚫 Autores excluidos del análisis: {sorted(excluded)}")

    base_sha = env["BASE_SHA"]
    head_sha = env["HEAD_SHA"]
    print(f"🔍 Recolectando estadísticas git ({base_sha[:7]}..{head_sha[:7]})...")
    git_stats = collect_git_stats(base_sha, head_sha, tp_dir, excluded)
    print(f"   Commits de alumnos: {git_stats['total_commits']}")
    if int(git_stats["excluded_count"]) > 0:
        print(f"   Commits de docentes excluidos: {git_stats['excluded_count']}")

    # Llamar a la API (con reintentos)
    print(f"🤖 Llamando a {MODEL} (hasta {MAX_RETRIES} intentos)...")
    prompt = build_prompt(tp_dir, rubric, source_files, readme, git_stats)

    client = anthropic.Anthropic(api_key=env["ANTHROPIC_API_KEY"])
    try:
        response = call_llm_with_retries(client, prompt)
    except RuntimeError as e:
        # Todos los reintentos fallaron — publicar comentario de error en el PR
        error_body = (
            f"## Revisión Automática — {tp_dir}\n\n"
            f"> ⚠️ La revisión LLM no pudo completarse.\n\n"
            f"**Error:** `{e}`\n\n"
            f"El docente puede re-ejecutar la revisión manualmente desde "
            f"[Actions → Revisión LLM]"
            f"(../../actions/workflows/llm_review.yml) "
            f"usando **workflow_dispatch**.\n\n"
            f"---\n*Revisión generada automáticamente — orientativa.*"
        )
        print(f"❌ {e}")
        print("💬 Publicando comentario de error en el PR...")
        post_pr_comment(
            env["PR_NUMBER"],
            env["GITHUB_REPOSITORY"],
            env["GITHUB_TOKEN"],
            error_body,
        )
        sys.exit(1)

    comment = response.content[0].text
    usage = response.usage
    cost_usd = (usage.input_tokens * 3 + usage.output_tokens * 15) / 1_000_000
    print(f"   Tokens: {usage.input_tokens:,} input / {usage.output_tokens:,} output")
    print(f"   Costo estimado: ~${cost_usd:.4f} USD")

    # Publicar comentario
    print(f"💬 Publicando comentario en PR #{env['PR_NUMBER']}...")
    post_pr_comment(
        env["PR_NUMBER"],
        env["GITHUB_REPOSITORY"],
        env["GITHUB_TOKEN"],
        comment,
    )


if __name__ == "__main__":
    main()
