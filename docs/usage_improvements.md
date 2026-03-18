# ContextBridge 使用改进

## 新增的 watch add 选项

为了解决大量文件索引时的日志输出问题，我们新增了以下选项：

### 1. 静默模式 (`--quiet`, `-q`)
减少日志输出，只显示关键信息：
```bash
cbridge watch add /path/to/docs --quiet
```

### 2. 后台执行 (`--background`, `-b`)
将索引操作放到后台执行，立即返回：
```bash
cbridge watch add /path/to/docs --background
```

### 3. 仅添加监控 (`--no-index`)
只添加到监控列表，不立即索引：
```bash
cbridge watch add /path/to/docs --no-index
```

### 4. 组合使用
```bash
# 后台静默执行
cbridge watch add /path/to/docs --background --quiet

# 仅添加监控，稍后手动索引
cbridge watch add /path/to/docs --no-index
cbridge index --path /path/to/docs --quiet
```

## 改进的索引命令

新的 `index` 命令支持指定路径和静默模式：

```bash
# 索引指定路径
cbridge index --path /path/to/docs

# 静默索引所有监控文件夹
cbridge index --quiet

# 静默索引指定路径
cbridge index --path /path/to/docs --quiet
```

## 日志输出优化

- 减少了成功文件的输出噪音
- 简化了错误信息显示
- 失败文件列表限制为前10个
- 将调试信息移至 DEBUG 级别

## 使用建议

1. **大量文件场景**：使用 `--background` 选项避免阻塞终端
2. **自动化脚本**：使用 `--quiet` 选项减少输出
3. **分步操作**：先用 `--no-index` 添加监控，再手动索引
4. **监控进度**：使用 `cbridge logs` 查看后台索引进度