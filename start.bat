@echo off
setlocal enabledelayedexpansion

REM Diretório do script
set SCRIPT_DIR=%~dp0
set SERVER_BIN=%SCRIPT_DIR%bedrock_server.exe
set SERVER_PROPS=%SCRIPT_DIR%server.properties

cd /d "%SCRIPT_DIR%" || (
    echo Erro: Não foi possível entrar no diretório %SCRIPT_DIR%
    exit /b 1
)

REM --- OTIMIZAÇÃO E LIMITES DE RECURSOS ---
REM No Windows não existe ulimit, então não aplicamos limites de RAM/arquivos aqui.

REM Verificar se o executável existe
if not exist "%SERVER_BIN%" (
    echo Erro: Executável bedrock_server não encontrado em %SERVER_BIN%
    exit /b 1
)

REM Definir portas padrão
set SERVER_PORT=19132
set SERVER_PORTV6=19133

REM Ler server.properties se existir
if exist "%SERVER_PROPS%" (
    for /f "tokens=1,2 delims==" %%a in (%SERVER_PROPS%) do (
        if "%%a"=="server-port" set SERVER_PORT=%%b
        if "%%a"=="server-portv6" set SERVER_PORTV6=%%b
    )
)

echo ==========================================
echo   A iniciar Minecraft Bedrock Server...
echo   Diretório: %SCRIPT_DIR%
echo   Porta IPv4 (UDP): %SERVER_PORT%
echo   Porta IPv6 (UDP): %SERVER_PORTV6%
echo   Prima Ctrl+C para parar o servidor
echo ==========================================
echo.

REM Aviso se a porta já estiver em uso (Windows não tem ss/lsof, usamos netstat)
for %%p in (%SERVER_PORT% %SERVER_PORTV6%) do (
    netstat -ano | findstr "%%p" >nul
    if not errorlevel 1 (
        echo ⚠️  AVISO: A porta %%p já está em uso!
        echo    Tenta parar o outro servidor ou editar server.properties
        echo.
    )
)

REM Executar servidor
"%SERVER_BIN%"
