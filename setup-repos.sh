#!/usr/bin/env bash
# setup-repos.sh
#
# Configura el secreto ANTHROPIC_API_KEY y los permisos de escritura
# de workflows para los repositorios de uno o varios cursos.
#
# Ejecutá sin argumentos para modo interactivo:
#   ./setup-repos.sh
#
# O pasá todo por argumentos (útil para automatizar):
#   ./setup-repos.sh --year 25 --courses 051,052 --groups 10 --key sk-ant-...
#
# La API key también puede venir de la variable de entorno ANTHROPIC_API_KEY.
#
# Requisitos:
#   - gh CLI instalado y autenticado (gh auth login)
#   - Permisos de admin sobre la organización utn-frba-ssl

set -euo pipefail

ORG="utn-frba-ssl"

# ── Colores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
die()   { error "$*"; exit 1; }

prompt() {
  # prompt <variable_name> <mensaje> [default]
  local var="$1" msg="$2" default="${3:-}"
  local display_default=""
  [[ -n "$default" ]] && display_default=" [${default}]"
  while true; do
    read -rp "$(echo -e "${BOLD}${msg}${display_default}: ${NC}")" value
    value="${value:-$default}"
    [[ -n "$value" ]] && break
    echo -e "${YELLOW}  El campo no puede estar vacío.${NC}"
  done
  printf -v "$var" '%s' "$value"
}

prompt_secret() {
  local var="$1" msg="$2"
  while true; do
    read -rsp "$(echo -e "${BOLD}${msg}: ${NC}")" value
    echo ""
    [[ -n "$value" ]] && break
    echo -e "${YELLOW}  El campo no puede estar vacío.${NC}"
  done
  printf -v "$var" '%s' "$value"
}

# ── Parsear argumentos opcionales ─────────────────────────────────────────────
YEAR=""
COURSES_RAW=""
GROUP_COUNT=""
API_KEY="${ANTHROPIC_API_KEY:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --year)    YEAR="$2";        shift 2 ;;
    --courses) COURSES_RAW="$2"; shift 2 ;;
    --groups)  GROUP_COUNT="$2"; shift 2 ;;
    --key)     API_KEY="$2";     shift 2 ;;
    *) die "Argumento desconocido: '$1'" ;;
  esac
done

# ── Verificar dependencias antes de pedir datos ────────────────────────────────
command -v gh &>/dev/null || die "'gh' CLI no está instalado. Instalalo desde https://cli.github.com/"
gh auth status &>/dev/null || die "No estás autenticado en gh. Ejecutá: gh auth login"

# ── Modo interactivo: pedir lo que falte ───────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}  Configuración de repositorios SSL — UTN FRBA${NC}"
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════════════${NC}"
echo ""

[[ -z "$YEAR" ]]        && prompt YEAR        "Año (2 dígitos, ej: 25)"
[[ -z "$COURSES_RAW" ]] && prompt COURSES_RAW "Cursos (separados por coma, ej: 051,052,001)"
[[ -z "$GROUP_COUNT" ]] && prompt GROUP_COUNT "Cantidad de grupos por curso (ej: 10)"
[[ -z "$API_KEY" ]]     && prompt_secret API_KEY "Anthropic API Key (sk-ant-...)"

# ── Validaciones ───────────────────────────────────────────────────────────────
[[ "$YEAR" =~ ^[0-9]{2}$ ]]      || die "El año debe tener exactamente 2 dígitos. Recibido: '$YEAR'"
[[ "$GROUP_COUNT" =~ ^[0-9]+$ ]] || die "La cantidad de grupos debe ser un número. Recibido: '$GROUP_COUNT'"
[[ "$GROUP_COUNT" -ge 1 ]]       || die "La cantidad de grupos debe ser al menos 1."
[[ -n "$API_KEY" ]]              || die "La API key no puede estar vacía."

# Parsear y validar cursos
IFS=',' read -ra COURSES <<< "$COURSES_RAW"
VALID_COURSES=()
for c in "${COURSES[@]}"; do
  c="${c// /}"  # quitar espacios
  [[ "$c" =~ ^[0-9]{3}$ ]] || die "Curso inválido: '$c'. Debe tener 3 dígitos (ej: 051)."
  VALID_COURSES+=("$c")
done
[[ ${#VALID_COURSES[@]} -ge 1 ]] || die "Debés indicar al menos un curso."

# ── Resumen antes de ejecutar ──────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Configuración a aplicar:${NC}"
info "Organización : $ORG"
info "Año          : $YEAR"
info "Cursos       : ${VALID_COURSES[*]}"
info "Grupos       : 01 → $(printf '%02d' "$GROUP_COUNT") por curso"
info "API Key      : ${API_KEY:0:12}…"
info "Total repos  : $((${#VALID_COURSES[@]} * GROUP_COUNT))"
echo ""
read -rp "$(echo -e "${BOLD}¿Continuar? [s/N]: ${NC}")" confirm
[[ "${confirm,,}" =~ ^(s|si|sí|y|yes)$ ]] || { echo "Cancelado."; exit 0; }
echo ""

# ── Función que configura un repositorio ──────────────────────────────────────
ERRORS=()
TOTAL=0
SUCCESS=0

configure_repo() {
  local full_repo="$1"
  TOTAL=$((TOTAL + 1))

  echo -e "${CYAN}── ${full_repo} ──${NC}"

  if ! gh repo view "$full_repo" &>/dev/null; then
    warn "Repositorio no encontrado, salteando."
    ERRORS+=("$full_repo: repositorio no encontrado")
    echo ""
    return
  fi

  local repo_ok=true

  if gh secret set ANTHROPIC_API_KEY \
      --repo "$full_repo" \
      --body "$API_KEY" 2>/dev/null; then
    ok "Secreto ANTHROPIC_API_KEY configurado"
  else
    warn "No se pudo configurar el secreto"
    ERRORS+=("$full_repo: error al setear secreto")
    repo_ok=false
  fi

  if gh api \
      --method PUT \
      "repos/${full_repo}/actions/permissions/workflow" \
      --field default_workflow_permissions=write \
      --field can_approve_pull_request_reviews=false \
      &>/dev/null; then
    ok "Permisos de workflow configurados (write)"
  else
    warn "No se pudieron configurar los permisos de workflow"
    ERRORS+=("$full_repo: error al configurar permisos de workflow")
    repo_ok=false
  fi

  $repo_ok && SUCCESS=$((SUCCESS + 1))
  echo ""
}

# ── Iterar cursos y grupos ─────────────────────────────────────────────────────
for course in "${VALID_COURSES[@]}"; do
  echo -e "${BOLD}Curso ${course}${NC}"
  echo ""
  for i in $(seq 1 "$GROUP_COUNT"); do
    GROUP=$(printf '%02d' "$i")
    configure_repo "${ORG}/${YEAR}-${course}-${GROUP}"
  done
done

# ── Resumen final ──────────────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════════════${NC}"
echo -e "  Resultado: ${GREEN}${SUCCESS} OK${NC}  /  ${RED}$((TOTAL - SUCCESS)) con problemas${NC}  /  ${TOTAL} total"
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo ""
  echo -e "${YELLOW}  Advertencias:${NC}"
  for e in "${ERRORS[@]}"; do
    echo -e "    ${RED}•${NC} $e"
  done
fi
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════════════${NC}"
echo ""
