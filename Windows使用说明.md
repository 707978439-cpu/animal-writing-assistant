# 动物习作AI智能助教 - Windows版本打包与使用说明

## 一、运行方式（无需打包）

1. 安装 Python 3.8+（下载地址：https://www.python.org/downloads/）
2. 双击 **启动.bat**，自动安装依赖并启动服务
3. 在浏览器中访问：http://127.0.0.1:5001

## 二、打包为独立EXE（无需安装Python即可运行）

### 方法：双击打包脚本

1. 确保Windows电脑已安装 Python 3.8+
2. 双击 **build_exe.bat**
3. 等待3-5分钟
4. 打包完成后，在 `dist/动物习作AI智能助教/` 文件夹中找到 `动物习作AI智能助教.exe`
5. 双击该exe即可运行

### 手动打包（若脚本失效）

```cmd
pip install flask openai pyinstaller
pyinstaller build_exe.spec
```

## 三、文件说明

- `build_exe.spec` — PyInstaller打包配置文件
- `build_exe.bat` — 一键打包脚本（双击运行）
- `启动.bat` — 直接运行脚本（需要Python环境）
- `dist/动物习作AI智能助教.exe` — 打包生成的独立程序

## 四、注意事项

- EXE文件首次启动可能被Windows Defender拦截，点击"更多信息"→"仍要运行"
- 打包后的EXE文件约 60-80MB（含Python运行环境）
- 运行EXE时需要联网（用于调用AI服务）
