@echo off
chcp 65001 >nul
echo ================================================
echo    BACKUP DO PROJETO GESTAO DE SALAS
echo ================================================
echo.

python backup.py

echo.
echo ================================================
echo    Backup concluido!
echo ================================================
pause
