# 问题 003：Hugo 本地主题替换后仍尝试下载远程模块

**创建日期：** 2026-09-10  
**状态：** ✅ 已解决  
**影响范围：** 内网环境使用本地主题目录的 Hugo 项目  
**关联问题：** [问题 001](./问题清单.md#问题-001内网环境-hugo-serve-启动失败)

---

## 问题描述

在按照问题 001 的方案配置本地主题替换后，执行 `hugo serve` 仍然提示正在下载模块：

```
hugo: downloading modules …
```

进程卡住，最终超时报错。

当时的 `hugo.yaml` 配置：

```yaml
module:
  imports:
    - path: github.com/pgsty/oink
      replacement: ./themes/oink  # 或用户自定义路径
```

---

## 问题分析过程

### 第一步：确认主题目录已存在

检查项目结构，确认主题文件已解压到正确位置：

```
oink-starter/
├── oink-main/
│   └── oink-main/
│       ├── theme.toml   ✅ 存在
│       ├── layouts/     ✅ 存在
│       ├── assets/      ✅ 存在
│       └── go.mod       ⚠️ 待检查
├── hugo.yaml
└── go.mod
```

### 第二步：分析 Hugo 模块替换机制

Hugo 的模块替换涉及**两个层面**：

| 层面 | 配置文件 | 作用 |
|------|---------|------|
| Hugo 层 | `hugo.yaml` 的 `replacement` 字段 | 告诉 Hugo 从本地路径加载主题文件 |
| Go 层 | `go.mod` 的 `replace` 指令 | 告诉 Go 模块系统使用本地路径，**不访问远程仓库** |

**关键发现：** 仅在 `hugo.yaml` 中设置 `replacement` 是不够的，Go 模块系统仍会尝试验证远程版本。

### 第三步：检查 go.mod 配置

查看项目根目录 `go.mod`：

```go
module github.com/pgsty/oink-starter

go 1.25.4

require github.com/pgsty/oink v1.0.0
```

**问题：** 缺少 `replace` 指令，Go 仍然尝试从 `github.com` 下载验证模块。

### 第四步：检查本地主题的 go.mod

查看 `oink-main/oink-main/go.mod`：

```go
module github.com/pgsty/oink

go 1.27.0
```

**问题：** 本地主题的 `go.mod` 也声明了 `go 1.27.0`，高于本地 Go 版本 1.25.4，触发 Go 工具链下载机制。

---

## 完整解决方案

### 步骤 1：在 go.mod 中添加 replace 指令

修改项目根目录 `go.mod`，添加 `replace` 指令：

```diff
 module github.com/pgsty/oink-starter

 go 1.25.4

-require github.com/pgsty/oink v1.0.0
+require github.com/pgsty/oink v1.0.0
+
+replace github.com/pgsty/oink => ./oink-main/oink-main
```

### 步骤 2：修正本地主题的 Go 版本

修改 `oink-main/oink-main/go.mod`，将 Go 版本降级为本地版本：

```diff
 module github.com/pgsty/oink

-go 1.27.0
+go 1.25.4
```

### 步骤 3：确保 hugo.yaml 的 replacement 路径正确

确认 `hugo.yaml` 中的 `replacement` 路径与实际主题目录匹配：

```yaml
module:
  imports:
    - path: github.com/pgsty/oink
      replacement: ./oink-main/oink-main  # 必须与实际解压路径一致
  hugoVersion:
    extended: true
    min: 0.160.1
```

---

## 验证结果

执行 `hugo serve` 后输出：

```
hugo: collected modules in 594 ms
Watching for changes in ...
Start building sites …
hugo v0.166.0-78400b4de8adc99273d3e674ed6c4d14c3bdf669 windows/amd64

Built in 375 ms
```

✅ 模块收集成功，不再尝试下载远程模块。

---

## 关键知识点

### Hugo 模块替换的双层机制

Hugo 使用 Go Modules 管理主题依赖，完整的本地替换需要同时配置两个层面：

```
┌─────────────────────────────────────────────────────────────┐
│  Hugo 层（hugo.yaml）                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  module.imports[].replacement: ./local/path         │   │
│  │  → 告诉 Hugo 从本地路径读取主题文件                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            +
┌─────────────────────────────────────────────────────────────┐
│  Go 层（go.mod）                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  replace github.com/xxx/theme => ./local/path       │   │
│  │  → 告诉 Go 不访问远程仓库，直接使用本地路径             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**两者缺一不可：**
- 只配置 Hugo 层：Go 仍会尝试验证远程版本
- 只配置 Go 层：Hugo 不知道从哪加载主题文件

### 嵌套 go.mod 的版本一致性

当主题本身也是一个 Go 模块（包含自己的 `go.mod`）时：

- 主题的 `go.mod` 中声明的 Go 版本也会触发工具链下载机制
- 需要将**所有相关 `go.mod`** 中的版本统一为本地已安装版本

---

## 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `go.mod` | 添加 `replace github.com/pgsty/oink => ./oink-main/oink-main` |
| `hugo.yaml` | `replacement` 路径修正为 `./oink-main/oink-main` |
| `oink-main/oink-main/go.mod` | `go 1.27.0` → `go 1.25.4` |

---

## 排查流程图

```
hugo serve 仍提示下载模块
         │
         ▼
   ┌─────────────────┐
   │ 主题目录是否存在？ │
   └─────────────────┘
         │
    ┌────┴────┐
    │ 否      │ 是
    │         │
    ▼         ▼
 解压主题   ┌─────────────────────┐
            │ go.mod 是否有 replace │
            └─────────────────────┘
                    │
               ┌────┴────┐
               │ 否      │ 是
               │         │
               ▼         ▼
          添加 replace  ┌───────────────────────┐
                       │ 主题 go.mod 版本是否 ≤  │
                       │ 本地 Go 版本？          │
                       └───────────────────────┘
                              │
                         ┌────┴────┐
                         │ 否      │ 是
                         │         │
                         ▼         ▼
                    降级主题     启动成功 ✅
                    go.mod 版本
```
