# OpenClaw 集成指南 (Skill 模式)

ContextBridge 可以作为原生 Skill 无缝集成到 OpenClaw 中。通过提供一个简单的 `SKILL.md` 文件，你可以赋予 OpenClaw 智能体瞬间读取和搜索本地文档的能力。

## 架构设计：为什么选择 SKILL.md？

OpenClaw 是一个强大的多渠道 AI 网关，它使用独特的基于 Prompt 的 Skill 系统。与编写复杂的 Node.js 或 Python 插件不同，OpenClaw 允许你使用简单的 Markdown 文件 (`SKILL.md`) 来定义 Skill。

1. **零代码集成**：你不需要编写任何集成代码。`SKILL.md` 文件只是告诉 AI *如何* 使用其现有的工具（如 `exec` 或 `bash`）与 ContextBridge 对话。
2. **原生兼容性**：这种方法利用了 OpenClaw 内置的工具执行能力，确保了最大的兼容性和稳定性。
3. **Token 极致优化**：AI 永远不会将整篇文档塞入 Prompt。它通过 API 接口只获取最相关的文本块（Chunks），极大节省 Token 并提高回答准确率。

---

## 第一步：启动 ContextBridge API 服务

在接入 OpenClaw 之前，你需要让 ContextBridge 在后台运行并提供 API 服务。

打开终端，运行以下命令：

```bash
# 启动 API 服务（默认绑定 127.0.0.1:9790）
cbridge serve
```

启动后，ContextBridge 会同时做两件事：
1. 启动 FastAPI 服务器，监听 `http://127.0.0.1:9790`。
2. 在后台启动 Smart Folder Watcher，实时监控你的本地文件夹变更。

你可以通过访问 `http://127.0.0.1:9790/docs` 查看完整的 API 文档（Swagger UI）。

---

## 第二步：创建 OpenClaw Skill

要集成 ContextBridge，你需要在 OpenClaw 工作区中创建一个新的 Skill。

1. 导航到你的 OpenClaw skills 目录（例如 `~/.openclaw/skills/` 或 `<workspace>/skills/`）。
2. 创建一个名为 `contextbridge` 的新文件夹。
3. 在此文件夹内，创建一个名为 `SKILL.md` 的文件，内容如下：

```markdown
---
name: contextbridge
description: 搜索并检索用户本地文档（Word、Excel、PDF、Markdown）中的信息。
metadata: { "openclaw": { "emoji": "📚", "requires": { "bins": ["curl"] } } }
---

# ContextBridge 本地知识库

你可以通过运行在 `http://127.0.0.1:9790` 的 ContextBridge API 访问用户的本地文档。

当用户询问可能存在于其本地文件中的信息时，你必须使用你的 `exec` 或 `bash` 工具来查询 ContextBridge API。

## 如何搜索文档

要搜索信息，请使用 `curl` 向 `/api/v1/search` 端点发送 POST 请求。

使用 `exec` 的示例：
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/search -H 'Content-Type: application/json' -d '{\"query\": \"2024年营销预算\", \"top_k\": 3}'"
}
```

API 将返回一个 JSON 数组，包含最相关的文本块，包括 `content` 和 `metadata.source` 文件路径。使用这些信息来回答用户的问题，并引用源文件。

## 如何管理监控的文件夹

如果用户要求将文件夹添加或从知识库中移除，请使用 `/api/v1/watch/directories` 端点。

添加文件夹：
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/watch/directories -H 'Content-Type: application/json' -d '{\"path\": \"/文件夹/的/绝对/路径\"}'"
}
```

检查当前正在监控哪些文件夹：
```json
{
  "command": "curl -s http://127.0.0.1:9790/api/v1/watch/status"
}
```
```

---

## 第三步：在 OpenClaw 中启用 Skill

放置好 `SKILL.md` 文件后，你需要确保智能体被允许使用它。

1. 打开你的 OpenClaw 配置文件（例如 `~/.openclaw/openclaw.json` 或你的工作区配置）。
2. 确保将 `contextbridge` 添加到智能体的 `tools.allow` 列表中，同时包含所需的 `exec` 或 `bash` 工具（或 `group:runtime`）。

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "allow": [
            "group:runtime",
            "contextbridge"
          ]
        }
      }
    ]
  }
}
```

---

## 真实工作流演示

假设用户在 OpenClaw 中提问：**“根据最新的 Q3 财务报表，我们的营销支出是多少？”**

1. **意图识别**：OpenClaw 的 LLM 分析问题，并读取 `contextbridge` Skill 的指令。
2. **Tool Calling**：LLM 决定使用 `exec` 工具运行 `curl` 命令来请求 ContextBridge API。
3. **API 响应**：ContextBridge 瞬间返回 3 个最相关的文本块，并附带来源文件 `Q3_Report.pdf`。
4. **最终生成**：LLM 综合这些数据，生成自然语言回答给用户，并附上引用来源。

如果在对话过程中，用户修改了本地的 `Q3_Report.pdf`，ContextBridge 的后台 Watcher 会瞬间重构该文档的向量。下一秒用户再次提问时，AI 就能立刻给出基于最新修改的回答，全程无需手动干预。

---

## 故障排查

* **API 连接失败**：请确保 `cbridge serve` 正在运行，且端口未被占用（默认 `9790`，如果被占用会自动尝试其他端口）。
* **搜索不到最新内容**：让 AI 检查监控状态，确认目标文件夹是否在监控列表中。如果不在，让 AI 添加它。
* **Curl 命令失败**：确保运行 OpenClaw 的机器上安装了 `curl`（Skill 元数据中指定了 `"requires": { "bins": ["curl"] }`）。
