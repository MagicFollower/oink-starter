<#
.SYNOPSIS
    移除指定目录下的法文 Markdown 文档。

.DESCRIPTION
    本脚本用于批量清理 Hugo 多语言站点中不再需要的法文内容文件。

    工作流程：
      1. 读取项目根目录下的 hugo.yaml 配置文件。
      2. 从 languages 配置块中提取法文语言标记（如 fr）。
         - 同时支持已启用的语言行（  fr:）和已注释的语言行（#  fr:）。
      3. 在指定的基础目录下递归查找所有匹配 .<标记>.md 后缀的文件。
      4. 逐一删除匹配文件，并输出详细的操作日志。

    Hugo 多语言文件命名规则：
      默认语言文件不带后缀（如 welcome.md），非默认语言文件带语言后缀
      （如 welcome.en.md、welcome.fr.md）。本脚本通过后缀匹配来定位
      目标语言的文件。

.PARAMETER BaseDir
    要扫描和清理的基础目录路径。
    默认为项目根目录下的 content 文件夹。
    可传入自定义路径以对其他 Hugo 项目执行相同操作。

.EXAMPLE
    # 使用默认路径（content/）
    .\remove-fr-docs.ps1

.EXAMPLE
    # 指定自定义基础目录
    .\remove-fr-docs.ps1 -BaseDir "E:\other-project\content"

.NOTES
    作者: 项目维护团队
    依赖: PowerShell 5.1+、项目根目录下必须存在 hugo.yaml 配置文件
#>
param(
    [string]$BaseDir = (Join-Path (Join-Path $PSScriptRoot "..") "content")
)

$ErrorActionPreference = "Stop"

# --- 定位 hugo.yaml 配置文件 ---
$hugoConfig = Join-Path (Join-Path $PSScriptRoot "..") "hugo.yaml"
if (-not (Test-Path $hugoConfig)) {
    Write-Error "找不到 hugo.yaml 配置文件: $hugoConfig"
    exit 1
}

# --- 从 languages 配置块中解析法文语言标记 ---
#     兼容两种格式：
#       已启用: "  fr:"  （两个空格缩进 + 键名）
#       已注释: "#  fr:" （井号 + 空格 + 键名）
$inLangs = $false
$langKey  = $null

foreach ($line in Get-Content $hugoConfig) {
    # 检测 languages 块的起始位置
    if ($line -match '^languages\s*:') {
        $inLangs = $true
        continue
    }
    if ($inLangs) {
        # 遇到非缩进、非注释的行说明已离开 languages 块
        if ($line -match '^[^\s#]' -and $line.Trim().Length -gt 0) { break }
        # 匹配语言键名，提取第二个分组作为候选值
        if ($line -match '^(\s{2}|#\s+)(\w+)\s*:') {
            $candidate = $Matches[2]
            if ($candidate -eq 'fr') {
                $langKey = $candidate
                break
            }
        }
    }
}

# 未在配置中找到法文语言标记，无需执行
if (-not $langKey) {
    Write-Host "[INFO] hugo.yaml 中未找到法文语言标记 (fr)，无需操作。"
    exit 0
}

# --- 扫描基础目录并删除匹配的法文文件 ---
$suffix   = ".$langKey.md"
$resolved = Resolve-Path $BaseDir -ErrorAction SilentlyContinue
if (-not $resolved) {
    Write-Error "基础目录不存在: $BaseDir"
    exit 1
}

$files = Get-ChildItem -Path $resolved -Recurse -File -Filter "*$suffix"

# 没有找到需要删除的文件
if ($files.Count -eq 0) {
    Write-Host "[INFO] 目录 $resolved 下未发现任何 $suffix 文件。"
    exit 0
}

# 逐个删除并记录日志
$count = 0
foreach ($f in $files) {
    Remove-Item $f.FullName -Force
    Write-Host "  已删除: $($f.FullName)"
    $count++
}

Write-Host ""
Write-Host "[完成] 共移除 $count 个法文文档（后缀: $suffix）。"

