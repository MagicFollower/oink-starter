# 问题 004：Hugo 标准版无法编译 SCSS/SASS 样式

**创建日期：** 2026-09-10  
**状态：** ✅ 已定位，待用户下载 Extended 版本  
**影响范围：** 所有使用 SCSS/SASS 样式的 Hugo 项目  
**关联问题：** [问题 001](./问题清单.md#问题-001内网环境-hugo-serve-启动失败)

---

## 问题描述

模块下载问题修复后，执行 `hugo serve` 构建站点时报错：

```
ERROR error building site: render: [en v1.0.0 guest] failed to render pages:
render of "/404" failed: "...\layouts\404.html:12:11": execute of template failed

TOCSS: failed to transform "/scss/main.scss" (text/x-scss).
Check your Hugo installation; you need the extended version to build SCSS/SASS
with transpiler set to 'libsass'.: this feature is not available in your current
Hugo version, see https://goo.gl/YMrWcn for more information
```

---

## 问题分析过程

### 第一步：解读错误信息

错误信息明确指出：

```
you need the extended version to build SCSS/SASS
this feature is not available in your current Hugo version
```

说明当前 Hugo 版本不支持 SCSS 编译功能。

### 第二步：确认当前 Hugo 版本

执行 `hugo env` 查看详细信息：

```
hugo v0.166.0-78400b4de8adc99273d3e674ed6c4d14c3bdf669 windows/amd64
BuildDate=2026-09-09T14:45:02Z VendorInfo=gohugoio
```

**关键发现：** 版本号中**没有** `+extended` 标识，确认安装的是标准版。

> Extended 版的版本号格式为：`hugo v0.166.0+extended windows/amd64`

### 第三步：确认项目需求

查看主题配置，项目使用了 SCSS 样式文件：

```
oink-main/oink-main/assets/scss/main.scss
```

Hugo 主题在 `head-css.html` 中调用 `.RelPermalink` 处理 SCSS 文件，需要 libsass 转译器支持。

### 第四步：对比 Hugo 版本功能差异

| 功能 | 标准版 | Extended 版 |
|------|--------|-------------|
| HTML 模板渲染 | ✅ | ✅ |
| Markdown 处理 | ✅ | ✅ |
| **SCSS/SASS 编译** | ❌ | ✅ |
| 图片处理（WebP） | 部分 | 完整 |
| PostCSS 处理 | ❌ | ✅ |

---

## 解决方案

### 步骤 1：下载 Hugo Extended 版本

访问 Hugo 官方 releases 页面：

```
https://github.com/gohugoio/hugo/releases
```

找到与当前版本匹配的 Extended 版本（推荐同版本号 v0.166.0）：

```
hugo_extended_0.166.0_windows-amd64.zip
```

> 如果内网无法访问 GitHub，需在有外网的机器上下载后拷贝。

### 步骤 2：替换现有 Hugo

1. 解压下载的 zip 文件，得到新的 `hugo.exe`
2. 备份当前版本（可选）：
   ```powershell
   Rename-Item "D:\Installation\hugo_0.166.0_windows-amd64\hugo.exe" "hugo_standard.exe"
   ```
3. 将新的 `hugo.exe` 放入同目录：
   ```
   D:\Installation\hugo_0.166.0_windows-amd64\hugo.exe
   ```

### 步骤 3：验证 Extended 版本

执行以下命令确认版本：

```powershell
hugo env
```

**预期输出**（包含 `+extended`）：

```
hugo v0.166.0+extended windows/amd64
BuildDate=2026-09-09T14:45:02Z VendorInfo=gohugoio
```

### 步骤 4：重新启动项目

```powershell
hugo serve
```

---

## 关键知识点

### Hugo 的两个发行版本

Hugo 官方提供两个版本：

| 版本 | 说明 |
|------|------|
| **Standard（标准版）** | 仅包含核心功能，体积小 |
| **Extended（扩展版）** | 额外包含 libsass 和 PostCSS 支持，可编译 SCSS/SASS |

### 如何快速区分版本

```powershell
# 方法一：查看版本字符串
hugo version
# 标准版：hugo v0.166.0-xxxxx windows/amd64
# 扩展版：hugo v0.166.0+extended windows/amd64

# 方法二：查看详细环境信息
hugo env
# 扩展版会在第一行显示 +extended
```

### 为什么 OINK 主题需要 Extended 版

OINK 主题的样式系统基于 SCSS：

```
oink-main/oink-main/
├── assets/
│   └── scss/
│       ├── main.scss        ← 主样式入口
│       ├── _variables.scss  ← 变量定义
│       └── _mixins.scss     ← 混入定义
└── layouts/
    └── _partials/
        └── head-css.html    ← 调用 TOCSS 处理 SCSS
```

模板中使用 Hugo 内置的 `resources.ToCSS` 函数编译 SCSS，该函数依赖 libsass，仅 Extended 版提供。

---

## 下载渠道汇总

| 渠道 | 地址 | 说明 |
|------|------|------|
| GitHub Releases | `https://github.com/gohugoio/hugo/releases` | 官方发布页 |
| Hugo 官网 | `https://gohugo.io/installation/` | 安装指南 |
| Chocolatey | `choco install hugo-extended` | Windows 包管理器 |
| Scoop | `scoop install hugo-extended` | Windows 包管理器 |

> 内网环境建议通过 GitHub Releases 页面下载 zip 包后手动拷贝。

---

## 修改文件清单

本次问题无需修改项目文件，仅需替换 Hugo 可执行文件：

| 操作 | 路径 |
|------|------|
| 替换前备份（可选） | `D:\Installation\hugo_0.166.0_windows-amd64\hugo_standard.exe` |
| 替换后 | `D:\Installation\hugo_0.166.0_windows-amd64\hugo.exe`（Extended 版） |
