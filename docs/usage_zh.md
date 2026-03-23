# ContextBridge 使用手册 📚

**ContextBridge** 是你的本地 AI 知识库助手。它让 Claude Code、Cursor 等 AI 工具直接读懂你电脑上的 Word、PDF、Excel 等文档——无需上传云端，所有数据本地处理，隐私零泄露。

## 快速开始（3 分钟上手）

### 第一步：安装

```bash
pip install cbridge-agent
```

### 第二步：初始化并启动

```bash
cbridge init
```

按提示选择：
1. **界面语言**：`zh`（中文）或 `en`（英文）
2. **工作区目录**：默认 `~/.cbridge`

初始化完成后，服务已在后台运行。

### 第三步：添加监控文件夹

```bash
cbridge watch add /{你的文档/文档目录}
```

添加后 ContextBridge 会自动索引该文件夹中的所有文档。

---

## 常用命令

### 启动/停止服务

如初始化时未启动服务，或需要手动控制：

```bash
cbridge start        # 启动后台监控服务（Watcher + 向量数据库）
cbridge serve        # 启动 API 服务（供外部工具调用）
cbridge stop         # 停止所有后台服务
```

### 管理监控目录

```bash
# 添加监控目录
cbridge watch add /path/to/documents

# 查看已监控目录
cbridge watch list

# 移除监控
cbridge watch remove /path/to/documents
```

### 🔍 命令行搜索测试

不用打开 AI 工具，直接在终端测试搜索效果：

```bash
# 自然语言查询
cbridge search "Q3 季度销售数据"
```

### 🌐 接入 AI 工具（MCP）

**Claude Code** 或 **Cursor** 用户，添加以下配置到 MCP 设置：

```json
{
  "mcpServers": {
    "context-bridge": {
      "command": "cbridge",
      "args": ["mcp"]
    }
  }
}
```

配置完成后，直接对 AI 说：
> "帮我总结一下预算表里的重点项目"

AI 会自动调用 ContextBridge 检索你的本地文档。

---

## 进阶配置

### 切换解析策略

ContextBridge 支持两种文档解析策略：

- **MarkItDown**（默认）
  - 轻量快速，资源占用低
  - 适用场景：日常文档处理

- **Docling**
  - 高精度，保留复杂排版
  - 适用场景：学术论文、复杂表格

在配置文件中修改解析策略：

```yaml
parser:
  pdf_strategy: "docling"  # 或 "markitdown"
```

### 重建索引

当需要强制重建向量索引时：

```bash
cbridge index
```

### 切换语言

```bash
cbridge lang en    # 切换英文
cbridge lang zh    # 切换中文
```

### 查看运行状态

```bash
cbridge status     # 查看服务状态
```

---

## 支持格式一览

- **PDF** (`.pdf`) — 支持扫描版（OCR）和文字版
- **Word** (`.docx`, `.doc`) — 保留标题层级结构
- **Excel** (`.xlsx`, `.xls`) — 解析表格数据为 Markdown 表格
- **PowerPoint** (`.pptx`, `.ppt`) — 提取每页内容
- **Markdown** (`.md`) — 原生支持
- **文本文件** (`.txt`, `.csv`) — 直接读取

---

## 常见问题

**Q: 文档数据会发送到云端吗？**
A: 不会。所有解析、索引、检索都在本地完成，无需联网，无需 API Key。

**Q: 支持多大体积的文档？**
A: 取决于本地内存，一般支持百页级 PDF 无压力。

**Q: 新增文件多久能被检索到？**
A: 文件保存后 1-2 秒内自动同步到索引。

---

## 需要帮助？

- 项目主页：https://github.com/whyischen/context-bridge
- 问题反馈：提交 GitHub Issue

