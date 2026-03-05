@echo off
echo ========================================
echo   Parar Servidor LDAP de Teste
echo ========================================
echo.

cd /d "%~dp0"

echo A parar container LDAP...
docker-compose down

echo.
echo Servidor LDAP parado!
echo.
pause
