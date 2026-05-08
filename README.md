# 🐾 动物习作AI智能助教

> 小学语文教师辅助工具 · 基于DeepSeek大模型 · MIT开源协议

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目简介

本工具是一款专为小学语文教师设计的AI辅助教学工具，聚焦**四年级动物类习作**个性化辅导。教师可在课堂上使用本工具辅助写作教学，包含写作闯关、好词好句墙、写作分析建议、互动问答、范文展示五大模块。

**定位：** 教师教学辅助工具，严格遵循《中小学生成式人工智能使用指南（2025年版）》规范。

## ✨ 功能特色

| 模块 | 说明 |
|------|------|
| 🎯 **写作闯关** | 5步引导式写作（选动物→外形→习性→故事→完成），带进度条和推荐词语 |
| 📚 **好词好句墙** | 4大分类好词库，支持课堂实时添加，有例句可展开 |
| 📝 **写作分析建议** | AI辅助分析习作，卡片分项展示，支持教师批注补充 |
| 💬 **互动问答** | 多轮对话式写作答疑 |
| 📖 **范文展示** | 预置优秀学生范文，支持展开阅读 |

## 🚀 快速开始

### macOS

1. 下载项目，双击 `启动.command`
2. 或双击 `dist/动物习作AI智能助教.app`
3. 在浏览器中访问 `http://127.0.0.1:5001`

### Windows

1. 确保已安装 Python 3.8+
2. 双击 `启动.bat`
3. 或运行 `python app.py`
4. 在浏览器中访问 `http://127.0.0.1:5001`

### 构建可执行文件

```bash
# macOS
pip install py2app
python setup.py py2app

# Windows
pip install pyinstaller
pyinstaller build_exe.spec
```

## 🛠️ 技术栈

- **AI引擎：** DeepSeek（deepseek-chat）
- **后端框架：** Python Flask
- **前端：** 原生 HTML/CSS/JavaScript
- **打包：** py2app（macOS）/ PyInstaller（Windows）
- **开源协议：** MIT

## 📁 项目结构

```
动物习作AI智能助教/
├── app.py                # Flask 主程序
├── config.py             # 配置文件
├── mock_responses.py     # 模拟AI回复生成器
├── requirements.txt      # Python依赖
├── templates/index.html  # 前端模板
├── static/css/style.css  # 样式文件
├── static/js/main.js     # 前端交互脚本
├── dist/                 # 打包输出目录
├── LICENSE               # 开源协议
└── README.md             # 本文件
```

## 📜 政策合规

本工具在设计上严格遵守以下政策法规：

- **《"人工智能+教育"行动计划》**（教育部等五部门，2026年4月）
- **《中小学生成式人工智能使用指南》**（中国教育学会，2025年5月）
- **《义务教育语文课程标准（2022年版）》**

核心合规措施：
- 明确定位为教师教学辅助工具
- 写作分析建议仅供教师参考，不替代教师评价
- 小学阶段须在教师指导下使用

## 👤 作者

**许志超** — 惠州市富民小学语文教师

- 创AI案例作品：《动物习作AI智能助教》
- 课题：2025fmkt007（5G课堂五维融合模式）

## 📄 开源说明

本项目采用 **MIT 开源协议**，欢迎 Fork、Star、提交 Issue。

如需引用或用于教学研究，请保留原作者署名。
