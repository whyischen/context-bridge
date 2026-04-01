---
name: local-context-bridge
description: 通过 ContextBridge CLI 搜索本地文档（PDF/Word/Excel/Markdown）。使用场景：(1) 用户询问本地文件中的具体数据/事实（如"2024 预算是多少"）; (2) 需要基于内部政策/流程/模板回答问题; (3) 用户明确要求搜索本地文档; (4) 涉及非通用知识的私人信息检索。核心原则：先搜索 ContextBridge 再回答。
metadata: { "openclaw": { "emoji": "🌉", "requires": { "bins": ["cbridge"] } } }
---

# ContextBridge 本地知识库

通过 `cbridge` CLI 搜索本地文档的语义内容。所有数据保留在本地，100% 隐私安全。

---

## 🚀 快速启动

### 1. 安装（首次）

```bash
pip install cbridge-agent
```

### 2. 初始化（首次）

```bash
cbridge init
```

### 3. 添加监控目录

```bash
cbridge watch add /path/to/documents
cbridge watch list
```

### 4. 搜索

```bash
cbridge search <关键词>
```

---

## 🎯 核心工作流

```mermaid
flowchart TD
    A([用户提问]) --> B{涉及本地/私人知识？}
    B -- 否 --> C[直接回答]
    B -- 是 --> D[提取核心关键词]
    D --> E[cbridge search <关键词>]
    E --> F{找到结果？}
    F -- 否 --> G[扩大关键词范围重试]
    G --> F
    F -- 是 --> H[评估片段是否足够]
    H -- 足够 --> I[基于片段回答 + 引用来源]
    H -- 不足 --> J[读取完整文档后回答]
    I --> K([结束])
    J --> K
```

---

## 💡 搜索最佳实践

### 关键词提取

| 推荐 ✅ | 避免 ❌ |
|---------|--------|
| `2024 营销预算` | `2024 年的营销预算是多少？` |
| `采购政策` | `我们公司的采购政策是什么` |
| `Python 编码规范` | `帮我找找 Python 的编码规范` |

### 迭代策略

1. **精确关键词** → 无结果 → **扩大范围**
2. 尝试同义词或相关术语
3. 最多重试 2-3 次

### 引用要求

始终标注来源：
- "根据 `budget.xlsx` 的内容..."
- "如 `employee_handbook.pdf` 所述..."

---

## 📋 完整命令参考

详见 [`references/cli-reference.md`](references/cli-reference.md)

---

## 🔧 故障排查

详见 [`references/troubleshooting.md`](references/troubleshooting.md)

---

## 📚 资源

- **GitHub**: <https://github.com/whyischen/context-bridge>
- **配置**: `~/.cbridge/config.yaml`
- **工作区**: `~/.cbridge/workspace`
