@echo off
setlocal
cd /d "%~dp0"

echo 🏫 신구대학교 식단 알리미 앱을 실행하는 중입니다...
python shingu_menu_app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ 앱 실행 중 오류가 발생했습니다.
    pause
)
endlocal
