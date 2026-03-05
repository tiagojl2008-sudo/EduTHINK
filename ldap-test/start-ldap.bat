@echo off
echo ========================================
echo   Iniciar Servidor LDAP de Teste
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] A verificar Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Docker nao instalado ou nao no PATH!
    echo Faca download em: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo Docker instalado! OK
echo.

echo [2/3] A iniciar container LDAP...
docker-compose up -d

echo.
echo [3/3] A aguardar servidor LDAP...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Servidor LDAP iniciado!
echo ========================================
echo.
echo Credenciais de teste:
echo   Username: tiago    Password: password
echo   Username: user1    Password: password
echo   Username: user2    Password: password
echo   Username: admin    Password: admin
echo.
echo Interface Web: https://localhost:6443
echo   Login: cn=admin,dc=test,dc=local
echo   Password: admin
echo.
echo Para parar: docker-compose down
echo ========================================
pause
