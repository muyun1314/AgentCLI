# AgentCLI

> 一键管理命令行 AI 智能体的桌面启动器

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)]()

---

## 功能

- **智能体管理** — 添加、编辑、删除、排序 AI CLI 工具
- **一键启动** — 支持 Windows Terminal / PowerShell / CMD 三种终端
- **快速安装** — 内置官方源和镜像源，一键安装/卸载
- **自动检测** — 自动扫描已安装的智能体并添加到列表
- **搜索过滤** — 按名称或命令快速定位
- **主题切换** — 深色/浅色模式，即时生效
- **多语言** — 中文 / English
- **自动更新** — 检测 GitHub 最新发行版并提醒更新

## 支持的智能体

| 名称 | 类型 | 说明 |
|------|------|------|
| MiMo | npm | @mimo-ai/cli |
| Claude Code | npm | @anthropic-ai/claude-code |
| Codex | npm | @openai/codex |
| Copilot | npm | @github/copilot |
| Aider | pip | aider-chat |
| Continue | npm | @continuedev/cli |
| Cline | npm | cline |
| Cursor | winget | Cursor AI IDE |
| Windsurf | winget | Codeium Windsurf |

## 安装

从 [Releases](https://github.com/muyun1314/AgentCLI/releases) 下载最新 `AgentCLI.exe`。

或从源码运行：

```bash
pip install pywebview
python app.pyw
```

## 技术栈

- **前端**: HTML/CSS/JS（CSS Grid + Flexbox + CSS Variables 主题系统）
- **后端**: Python + pywebview
- **打包**: PyInstaller
- **零外部 UI 依赖** — 单文件 HTML 内嵌全部样式和逻辑

## 项目结构

```
AgentCLI/
├── app.pyw           # 主程序入口（pywebview + Python 后端）
├── web/
│   └── index.html    # 前端 UI（单文件内嵌 CSS/JS）
├── run.bat           # 一键启动脚本
├── build.bat         # PyInstaller 打包脚本
└── config.json       # 用户配置（自动生成）
```

## 许可证

MIT — 详见 [LICENSE](LICENSE)
