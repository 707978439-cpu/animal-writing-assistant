@echo off
chcp 65001 >nul
title 动物习作AI智能助教
echo ========================================
echo   动物习作AI智能助教 正在启动...
echo ========================================
echo.
echo 请在浏览器中打开：
echo   http://127.0.0.1:5001
echo.
echo 按 Ctrl+C 可停止服务
echo ========================================
echo.

start http://127.0.0.1:5001
python app.py

pause
