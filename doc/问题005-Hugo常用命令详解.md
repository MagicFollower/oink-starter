# 问题 005：Hugo 常用命令详解

**创建日期：** 2026-09-10  
**状态：** ✅ 知识整理  
**影响范围：** Hugo 项目日常开发与调试  

---

## 一、hugo serve 与 hugo serve -D 的区别

| 命令 | 功能 | 适用场景 |
|------|------|---------|
| `hugo serve` | 启动开发服务器，**仅渲染已发布内容** | 正式预览、发布前检查 |
| `hugo serve -D` | 启动开发服务器，**同时渲染草稿内容** | 编写草稿时实时预览 |

### 关键区别：草稿（Draft）处理

Hugo 的 Markdown 文件头部有 `draft` 字段：

```yaml
---
title: "我的文章"
draft: true    # 草稿状态
---
```

| 命令 | `draft: true` 的文章 | `draft: false` 或无此字段 |
|------|---------------------|------------------------|
| `hugo serve` | ❌ 不显示 | ✅ 显示 |
| `hugo serve -D` | ✅ 显示 | ✅ 显示 |

---

## 二、如何停止 Hugo 服务器

在终端中按 **`Ctrl + C`** 即可停止：

```
^C
Received signal: interrupt
Shutting down...
```

---

## 三、常用 Hugo 命令详解

### 1. 构建类命令

| 命令 | 功能 | 常用参数 |
|------|------|---------|
| `hugo` | 构建站点，输出到 `public/` 目录 | 无实时预览，一次性生成 |
| `hugo --minify` | 构建并压缩 HTML/CSS/JS | 生产环境部署 |
| `hugo --gc` | 构建时清理未使用的缓存文件 | 清理优化 |
| `hugo -e production` | 指定环境为 production | 使用生产环境配置 |

**示例：**

```powershell
# 生产环境构建（压缩 + 清理）
hugo --minify --gc -e production
```

---

### 2. 开发服务器命令

| 命令 | 功能 |
|------|------|
| `hugo serve` | 启动开发服务器（默认端口 1313） |
| `hugo serve -D` | 启动服务器，包含草稿 |
| `hugo serve --bind 0.0.0.0` | 允许局域网其他设备访问 |
| `hugo serve -p 8080` | 指定端口为 8080 |
| `hugo serve --disableFastRender` | 禁用快速渲染（完整重建） |
| `hugo serve --navigateToChanged` | 文件修改后自动跳转到变更页面 |

**局域网访问示例：**

```powershell
# 启动后，其他设备可通过 http://你的IP:1313 访问
hugo serve --bind 0.0.0.0
```

---

### 3. 内容管理类命令

| 命令 | 功能 |
|------|------|
| `hugo new content/post/my-post.md` | 创建新内容 |
| `hugo new content/post/my-post.md -k posts` | 使用指定原型（archetype）创建 |
| `hugo undraft content/post/my-post.md` | 将草稿标记为已发布 |

**创建内容示例：**

```powershell
# 创建一篇博客文章
hugo new content/blog/my-first-post.md

# 创建后文件内容：
# ---
# title: "My First Post"
# date: 2026-09-10
# draft: true    ← 默认为草稿
# ---
```

---

### 4. 模块管理命令

| 命令 | 功能 |
|------|------|
| `hugo mod get` | 下载/更新模块依赖 |
| `hugo mod tidy` | 清理未使用的模块依赖 |
| `hugo mod vendor` | 将模块复制到 `_vendor/` 目录 |
| `hugo mod graph` | 显示模块依赖关系图 |

**内网开发常用：**

```powershell
# 将模块本地化（内网推荐）
hugo mod vendor
```

---

### 5. 调试与诊断命令

| 命令 | 功能 |
|------|------|
| `hugo env` | 显示 Hugo 环境信息（版本、平台等） |
| `hugo config` | 显示当前站点配置 |
| `hugo list drafts` | 列出所有草稿 |
| `hugo list future` | 列出未来发布日期的内容 |
| `hugo list expired` | 列出已过期的内容 |
| `hugo list all` | 列出所有内容 |

**调试示例：**

```powershell
# 查看所有草稿
hugo list drafts

# 查看完整配置
hugo config | more
```

---

## 四、常用参数速查表

| 参数 | 缩写 | 功能 |
|------|------|------|
| `--draft` | `-D` | 包含草稿内容 |
| `--buildDrafts` | | 同 `-D` |
| `--buildFuture` | `-F` | 包含未来发布的内容 |
| `--buildExpired` | `-E` | 包含已过期内容 |
| `--port` | `-p` | 指定端口 |
| `--bind` | | 绑定地址（0.0.0.0 允许局域网） |
| `--baseURL` | `-b` | 指定 baseURL |
| `--destination` | `-d` | 指定输出目录 |
| `--verbose` | `-v` | 显示详细日志 |
| `--cleanDestinationDir` | | 构建前清理输出目录 |
| `--watch` | `-w` | 监听文件变化（serve 默认开启） |
| `--minify` | | 压缩输出 |
| `--gc` | | 清理缓存 |
| `--environment` | `-e` | 指定环境（development/production） |
| `--theme` | `-t` | 指定主题 |

---

## 五、典型工作流

```powershell
# 1. 开发阶段：启动服务器，包含草稿
hugo serve -D

# 2. 预览阶段：仅预览已发布内容
hugo serve

# 3. 局域网测试：允许其他设备访问
hugo serve --bind 0.0.0.0 -p 8080

# 4. 生产构建：压缩 + 清理 + 指定环境
hugo --minify --gc -e production

# 5. 检查草稿列表
hugo list drafts
```

---

## 六、命令分类总览

```
hugo
├── 构建类
│   ├── hugo                    → 构建站点
│   ├── hugo --minify           → 压缩构建
│   └── hugo --gc               → 清理缓存
│
├── 开发服务器
│   ├── hugo serve              → 启动服务器
│   ├── hugo serve -D           → 包含草稿
│   └── hugo serve --bind 0.0.0.0 → 局域网访问
│
├── 内容管理
│   ├── hugo new                → 创建内容
│   └── hugo undraft            → 发布草稿
│
├── 模块管理
│   ├── hugo mod get            → 下载模块
│   ├── hugo mod tidy           → 清理模块
│   └── hugo mod vendor         → 本地化模块
│
└── 调试诊断
    ├── hugo env                → 环境信息
    ├── hugo config             → 站点配置
    └── hugo list drafts        → 列出草稿
```
