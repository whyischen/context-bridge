# Agent Guidelines (AGENTS.md)

## 项目结构

```
context-bridge/
├── core/                   # 核心基础设施
│   ├── config.py           # 配置管理
│   ├── factories.py        # 工厂函数
│   └── ...
├── skills/
│   └── local-context-bridge/  # Skill 适配层
│       ├── skill.py        # Skill 主类
│       ├── setup.py        # 设置类
│       ├── SKILL.md        # 文档
│       └── version.py      # Skill 版本号
├── .agent-cache/           # Agent 临时文件（不提交）
├── AGENTS.md              # 本文件
└── .gitignore             # Git 忽略规则
```

## Agent 临时文件管理

### 临时文件目录
```
.agent-cache/
├── memory/          # Agent 临时记忆文件
├── context/         # 上下文缓存
└── temp/            # 临时工作文件
```

### 使用规则
1. 所有临时文件存放在 `.agent-cache/` 目录
2. 不提交到 Git 仓库
3. 可随时删除，不影响项目功能
4. 用于存储：
   - 分析结果缓存
   - 上下文记忆
   - 临时工作文件
   - 调试信息

### 文件命名规范
- 格式：`{task}_{timestamp}.md` 或 `{task}_{id}.json`
- 示例：`refactor_20260316_143000.md`