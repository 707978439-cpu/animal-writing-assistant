@echo off
chcp 65001 >nul
echo ========================================
echo   动物习作AI智能助教 - Windows打包工具
echo ========================================
echo.

:: 检查Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: 检查Python版本
python --version | findstr "3." >nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 需要Python 3.x版本
    pause
    exit /b 1
)

echo [1/3] 安装依赖包...
pip install flask openai pyinstaller -q
echo.

echo [2/3] 开始打包为EXE...
echo 此过程可能需要3-5分钟，请耐心等待...
echo.

pyinstaller build_exe.spec

echo.
echo [3/3] 打包完成！
echo.
echo 生成文件位置：dist\动物习作AI智能助教\
echo 双击"动物习作AI智能助教.exe"即可运行
echo.
echo 启动后请在浏览器中访问：http://127.0.0.1:5001
echo.
pause
