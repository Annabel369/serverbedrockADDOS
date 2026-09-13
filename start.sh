#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_BIN="$SCRIPT_DIR/bedrock_server"
SERVER_PROPS="$SCRIPT_DIR/server.properties"

cd "$SCRIPT_DIR" || { echo "Erro: Não foi possível entrar no diretório $SCRIPT_DIR"; exit 1; }

if [ ! -f "$SERVER_BIN" ]; then
    echo "Erro: Executável bedrock_server não encontrado em $SERVER_BIN"
    exit 1
fi

if [ ! -x "$SERVER_BIN" ]; then
    echo "A dar permissão de execução ao bedrock_server..."
    chmod +x "$SERVER_BIN"
fi

SERVER_PORT="19132"
SERVER_PORTV6="19133"
if [ -f "$SERVER_PROPS" ]; then
    SERVER_PORT=$(grep -E '^server-port=' "$SERVER_PROPS" | cut -d'=' -f2)
    SERVER_PORTV6=$(grep -E '^server-portv6=' "$SERVER_PROPS" | cut -d'=' -f2)
fi

check_port() {
    local port="$1"
    if command -v ss &>/dev/null; then
        ss -ulnp 2>/dev/null | grep -q ":${port} " && return 1
        ss -tlnp 2>/dev/null | grep -q ":${port} " && return 1
    elif command -v lsof &>/dev/null; then
        lsof -i ":${port}" -sTCP:LISTEN,UDP &>/dev/null && return 1
    fi
    return 0
}

echo "=========================================="
echo "  A iniciar Minecraft Bedrock Server..."
echo "  Diretório: $SCRIPT_DIR"
echo "  Porta IPv4 (UDP): $SERVER_PORT"
echo "  Porta IPv6 (UDP): $SERVER_PORTV6"
echo "  Prima Ctrl+C para parar o servidor"
echo "=========================================="
echo ""

for port in "$SERVER_PORT" "$SERVER_PORTV6"; do
    if ! check_port "$port"; then
        echo "⚠️  AVISO: A porta $port já está em uso!"
        echo "   Tenta parar o outro servidor ou editar server.properties"
        echo ""
    fi
done

exec "$SERVER_BIN"
