# 问题 002：如何查看本地 Go 和 Hugo 的安装路径

**创建日期：** 2026-09-10  
**状态：** ✅ 已解决  
**影响范围：** 所有 Windows 开发环境  

---

## 问题描述

在内网排查环境问题时，需要确认本地安装的 Go 和 Hugo 的具体可执行文件路径（绝对路径），以便：

- 确认实际使用的版本来源，避免 PATH 中存在多个版本导致冲突
- 在内网离线部署时，明确需要拷贝或引用的目标路径
- 配置 IDE 或 CI 工具时提供准确的二进制路径

---

## 解决方案

### 方法一：PowerShell Get-Command（推荐）

```powershell
# 查看 Go 路径
Get-Command go | Select-Object -ExpandProperty Source

# 查看 Hugo 路径
Get-Command hugo | Select-Object -ExpandProperty Source
```

**示例输出：**

```
C:\Program Files\Go\bin\go.exe
D:\Installation\hugo_0.166.0_windows-amd64\hugo.exe
```

---

### 方法二：where.exe（列出 PATH 中所有匹配项）

```powershell
where.exe go
where.exe hugo
```

> 适用场景：怀疑 PATH 中存在多个同名可执行文件时，可列出所有匹配路径，优先级从上到下递减。

---

### 方法三：CMD 环境下的 where 命令

```cmd
where go
where hugo
```

---

### 方法四：查看版本信息（辅助确认）

```powershell
go version
hugo version
```

**示例输出：**

```
go version go1.25.4 windows/amd64
hugo v0.166.0-78400b4de8adc99273d3e674ed6c4d14c3bdf669 windows/amd64 BuildDate=2026-09-09T14:45:02Z VendorInfo=gohugoio
```

---

## 当前环境实际路径

| 工具 | 绝对路径 |
|------|--------|
| Go | `C:\Program Files\Go\bin\go.exe` |
| Hugo | `D:\Installation\hugo_0.166.0_windows-amd64\hugo.exe` |
