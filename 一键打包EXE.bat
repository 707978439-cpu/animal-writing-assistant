@echo off
chcp 65001 >nul
title 动物习作AI智能助教 - Windows一键打包

echo ========================================
echo   动物习作AI智能助教
echo   Windows 一键打包工具
echo ========================================
echo.

:: 检查Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [1/4] 下载Python...
    start https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    echo 请安装Python 3.8+（安装时勾选"Add Python to PATH"）
    echo 安装完成后重新运行本脚本
    pause
    exit /b 1
)

echo [1/4] 安装依赖包...
pip install flask openai httpx httpcore charset-normalizer urllib3 certifi idna sniffio pyinstaller -q
echo  完成
echo.

echo [2/4] 复制模板和静态文件...
echo  完成
echo.

echo [3/4] 打包为独立EXE（约3-5分钟）...
pyinstaller build_exe.spec --noconfirm
echo.
if exist dist\动物习作AI智能助教\动物习作AI智能助教.exe (
    echo [4/4] 打包成功！
    echo.
    echo ========================================
    echo   生成文件：dist\动物习作AI智能助教\
    echo   文件名：动物习作AI智能助教.exe
    echo   大小：约70MB（含Python运行环境）
    echo ========================================
    echo.
    echo 使用方法：
    echo   1. 双击"动物习作AI智能助教.exe"
    echo   2. 浏览器自动打开 http://127.0.0.1:5001
    echo.
    echo 注意：首次运行需要联网（调用AI服务）
) else (
    echo [错误] 打包失败，请检查报错信息
)

echo.
pause
