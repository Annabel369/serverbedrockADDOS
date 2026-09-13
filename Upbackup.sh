#!/bin/bash
#
# Upbackup.sh - Faz backup ou restaura o servidor Minecraft Bedrock
#
# USO:
#   ./Upbackup.sh                      # Faz backup para ../bedrock_backups/
#   ./Upbackup.sh backup               # O mesmo que acima
#   ./Upbackup.sh list                 # Lista backups existentes
#   ./Upbackup.sh restore <pasta> <destino>
#        Exemplo:
#        ./Upbackup.sh restore ../bedrock_backups/2026-09-13_14-30-00/  ../bedrock-server-NOVA/
#
#  Passos para atualizar servidor:
#   1) ./Upbackup.sh                        # Faz backup do servidor ATUAL
#   2) Extrai a NOVA versão bedrock-server-1.XX.XX.XX/  para a pasta mãe
#   3) ./Upbackup.sh restore ../bedrock_backups/<pasta_do_ultimo_backup>/  ../bedrock-server-1.XX.XX.XX/
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOTHER_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_BASE="$MOTHER_DIR/bedrock_backups"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"

# === Cores ===
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[AVISO]${NC} $*"; }
err()   { echo -e "${RED}[ERRO]${NC} $*"; }

usage() {
    cat <<EOF
Upbackup.sh - Backup e restauro de servidor Minecraft Bedrock

Uso:
  $0                      Cria um backup completo
  $0 backup               O mesmo
  $0 list                 Lista todos os backups
  $0 restore <BACKUP> <DESTINO>
      Restaura um backup numa pasta (ex: nova versão do servidor)
      Ex.: $0 restore $BACKUP_BASE/YYYY-MM-DD_HH-MM-SS/  ../bedrock-server-NEW/
EOF
}

# Itens que o script salva (adiciona aqui se quiseres mais ficheiros)
FILES=(
    "server.properties"
    "permissions.json"
    "allowlist.json"
    "valid_known_packs.json"
    "packetlimitconfig.json"
    "profanity_filter.wlist"
)

FOLDERS=(
    "worlds"
    "behavior_packs"
    "resource_packs"
    "definitions"
    "config"
    "data"
)

# === FUNÇÕES ===

ensure_not_running() {
    if pgrep -f "bedrock_server" >/dev/null 2>&1; then
        warn "O servidor bedrock_server está a correr!"
        warn "Fecha-o primeiro (Ctrl+C no terminal ou: pkill -f bedrock_server)"
        warn "Continuar com o servidor ligado pode corromper o backup."
        read -rp $'Continuar mesmo assim? (s/N): ' ans
        [[ "${ans,,}" != "s" ]] && { info "Cancelado pelo utilizador."; exit 0; }
    fi
}

do_backup() {
    ensure_not_running
    BACKUP_DIR="$BACKUP_BASE/$TIMESTAMP"
    mkdir -p "$BACKUP_DIR"

    info "A fazer backup do servidor: $SCRIPT_DIR"
    info "Destino do backup:   $BACKUP_DIR"
    echo ""

    # Ficheiros
    for f in "${FILES[@]}"; do
        if [ -e "$SCRIPT_DIR/$f" ]; then
            cp -a "$SCRIPT_DIR/$f" "$BACKUP_DIR/"
            ok "  ficheiro  $f"
        else
            warn "  ficheiro  $f  (não existe, a saltar)"
        fi
    done

    # Pastas
    for d in "${FOLDERS[@]}"; do
        if [ -d "$SCRIPT_DIR/$d" ]; then
            cp -a "$SCRIPT_DIR/$d" "$BACKUP_DIR/"
            local count
            count=$(find "$SCRIPT_DIR/$d" -type f 2>/dev/null | wc -l)
            ok "  pasta     $d/  ($count ficheiros)"
        else
            warn "  pasta     $d/  (não existe, a saltar)"
        fi
    done

    # Informação do servidor
    {
        echo "Data do backup: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Pasta de origem: $SCRIPT_DIR"
        if [ -f "$SCRIPT_DIR/server.properties" ]; then
            echo "server-port:     $(grep -E '^server-port='     "$SCRIPT_DIR/server.properties"     | cut -d= -f2)"
            echo "gamemode:        $(grep -E '^gamemode='        "$SCRIPT_DIR/server.properties"     | cut -d= -f2)"
            echo "server-name:     $(grep -E '^server-name='     "$SCRIPT_DIR/server.properties"     | cut -d= -f2)"
            echo "allow-cheats:    $(grep -E '^allow-cheats='    "$SCRIPT_DIR/server.properties"     | cut -d= -f2)"
            echo "allow-list:      $(grep -E '^allow-list='      "$SCRIPT_DIR/server.properties"     | cut -d= -f2)"
        fi
        echo ""
        echo "Operadores (permissions.json):"
        if [ -f "$SCRIPT_DIR/permissions.json" ]; then
            python3 -c "import json; d=json.load(open('$SCRIPT_DIR/permissions.json')); [print('  - xuid='+x['xuid']+' perm='+x['permission']) for x in d]" 2>/dev/null || \
            cat "$SCRIPT_DIR/permissions.json"
        fi
        echo ""
        echo "Allowlist:"
        if [ -f "$SCRIPT_DIR/allowlist.json" ]; then
            python3 -c "import json; d=json.load(open('$SCRIPT_DIR/allowlist.json')); [print('  - '+x['name']+' (xuid='+x['xuid']+')') for x in d]" 2>/dev/null || \
            cat "$SCRIPT_DIR/allowlist.json"
        fi
    } > "$BACKUP_DIR/INFO_BACKUP.txt"
    ok "  meta      INFO_BACKUP.txt"

    # Tamanho total
    SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo ""
    ok "Backup completo!  Tamanho: $SIZE"
    info "Pasta do backup: $BACKUP_DIR"
    info ""
    info "Para restaurar numa nova versão:"
    info "  $0 restore $BACKUP_DIR  ../bedrock-server-NOVA-VERSAO/"
}

list_backups() {
    if [ ! -d "$BACKUP_BASE" ]; then
        warn "Ainda não existe nenhum backup em: $BACKUP_BASE"
        return 0
    fi
    info "Backups existentes em $BACKUP_BASE:"
    echo ""
    ls -1dt "$BACKUP_BASE"/*/ 2>/dev/null | while read -r d; do
        size=$(du -sh "$d" 2>/dev/null | cut -f1)
        info_txt=""
        [ -f "$d/INFO_BACKUP.txt" ] && info_txt=" - $(head -n1 "$d/INFO_BACKUP.txt" | cut -c1-80)"
        ok "  $(basename "$d")  (${size})${info_txt}"
    done
}

do_restore() {
    local SRC="$1"
    local DST="$2"

    [ -z "$SRC" ] && { err "Falta a pasta de origem do backup (1º argumento)"; usage; exit 1; }
    [ -z "$DST" ] && { err "Falta a pasta de destino (2º argumento, ex: ../bedrock-server-1.XX.XX.XX/)"; usage; exit 1; }

    SRC="$(cd "$SRC" 2>/dev/null && pwd)"
    if [ -z "$SRC" ] || [ ! -d "$SRC" ]; then
        err "Pasta de backup inválida ou não existe: $1"; exit 1;
    fi

    if [ ! -f "$SRC/server.properties" ]; then
        err "A pasta $SRC não parece conter um backup válido (server.properties não encontrado)"; exit 1;
    fi

    if [ ! -d "$DST" ]; then
        warn "A pasta de destino não existe. Criar $DST ?"
        read -rp $'Criar pasta destino? (S/n): ' ans2
        [[ "${ans2,,}" != "n" ]] && mkdir -p "$DST"
        if [ ! -d "$DST" ]; then err "Impossível criar destino $DST"; exit 1; fi
    fi
    DST="$(cd "$DST" && pwd)"

    if pgrep -f "bedrock_server" >/dev/null 2>&1; then
        warn "Existe servidor bedrock_server a correr."
        warn "Fecha o servidor ANTES de restaurar para não corromper o mundo."
        read -rp $'Continuar? (s/N): ' ans3
        [[ "${ans3,,}" != "s" ]] && exit 0
    fi

    info "A restaurar backup"
    info "  Origem:  $SRC"
    info "  Destino: $DST"
    echo ""

    for f in "${FILES[@]}"; do
        if [ -e "$SRC/$f" ]; then
            cp -a "$SRC/$f" "$DST/"
            ok "  restaurado ficheiro: $f"
        fi
    done

    for d in "${FOLDERS[@]}"; do
        if [ -d "$SRC/$d" ]; then
            if [ -d "$DST/$d" ]; then
                warn "  $d/ já existe no destino - mesclar (substituir apenas arquivos do backup)"
            fi
            cp -a "$SRC/$d"/* "$DST/$d/" 2>/dev/null || cp -a "$SRC/$d" "$DST/"
            local count
            count=$(find "$SRC/$d" -type f 2>/dev/null | wc -l)
            ok "  restaurado pasta:    $d/  ($count ficheiros)"
        fi
    done

    if [ -f "$SRC/INFO_BACKUP.txt" ]; then
        cp -a "$SRC/INFO_BACKUP.txt" "$DST/INFO_BACKUP_$(date +%Y-%m-%d_%H-%M-%S).txt"
    fi

    echo ""
    ok "Restauração concluída!"
    info "Próximos passos:"
    info "  1) cd $DST"
    info "  2) chmod +x bedrock_server  (se a nova versão ainda não tiver)"
    info "  3) Copia o teu start.sh (ou faz um novo) para dentro da nova pasta"
    info "  4) ./start.sh   para arrancar a NOVA versão com os TEUS dados"
}

# === MAIN ===
ACTION="${1:-backup}"
case "$ACTION" in
    -h|--help|help|ajuda)
        usage; exit 0 ;;
    backup)
        do_backup ;;
    list|ls)
        list_backups ;;
    restore|restaurar)
        do_restore "$2" "$3" ;;
    *)
        err "Acção inválida: $ACTION"
        usage; exit 1 ;;
esac
