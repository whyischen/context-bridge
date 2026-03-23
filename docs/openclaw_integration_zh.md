# OpenClaw 集成指南

通过 ContextBridge 原生提供的 `local-context-bridge` Skill，你可以轻松地将本地知识库接入 [OpenClaw](https://openclaw.com/) (或相关的 AI 平台)。
只需提供一个简单的 `SKILL.md` 文件，即可赋予 OpenClaw 智能体瞬间读取、检索和理解你本地文档的能力。

---

## 📦 安装 Skill

ContextBridge 的原生技能已发布至[ClawHub.ai](https://clawhub.ai/)。我们提供两种安装方式：

### ✨ 方式一：通过对话安装（最简单）

如果你已经在运行 OpenClaw，你可以直接通过自然语言让 AI 替你完成安装：

> **💬 对话示例：**
> _"为我安装 local-context-bridge-cn skill"_

OpenClaw 会自动解析意图并引导你完成后续的安装流程。

### 💻 方式二：通过命令行安装（推荐开发者）

🛠 前置准备

在开始集成之前，请确保：

1. **ContextBridge 已在本地运行**（请参考 [快速开始](#) 启动你的本地服务）。
2. 本地已安装 [Node.js](https://nodejs.org/)（用于执行 npm 安装命令）。

使用 ClawHub CLI 工具进行全局安装：

```bash
# 1. 全局安装 ClawHub CLI
npm install -g clawhub@latest

# 2. 安装 local-context-bridge 技能
clawhub install local-context-bridge
```

---

## 🚀 开始使用

配置完成！现在你的 OpenClaw 已经长出了“窥探”本地文件的眼睛。你可以随时向 AI 提问：

- 🔍 _"利用 local-context-bridge，帮我搜索一下本地文档中关于 API 鉴权的配置说明。"_
- 📖 _"读取我本地的 `README.md`，并总结出项目的快速启动步骤。"_
- 💡 _"根据本地库中的错误码文档，告诉我 `Error 5003` 是什么原因导致的？"_

---

## ❓ 常见问题 (FAQ)

**Q: OpenClaw 提示无法连接到本地服务怎么办？**

A: 请检查你的 ContextBridge 服务是否已在后台正常运行，并核对 `SKILL.md` 中的端口号是否正确。