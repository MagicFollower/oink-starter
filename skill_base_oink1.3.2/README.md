# replicate-doc-site 技能（OINK v1.3.2 基线）

本目录是 `replicate-doc-site` 技能的 **OINK v1.3.2 基线副本**：判据脚本、写作规范与自证夹具沿用 1.0.0 基线的成熟结构，内置主题与版本相关事实全部更新到 OINK 1.3.2 实测口径。新复刻项目默认用这一份；目标站点明确要求旧版 OINK 行为时用 `../skill_base_oink1.0.0/`（两份技能结构完全相同，仅主题副本与版本相关事实不同）。

- 技能主体：`replicate-doc-site/SKILL.md`（流程主文，从 Step 0 到验收）
- 主题本体：`replicate-doc-site/assets/theme/oink-main/oink-main/`（OINK **v1.3.2**，1,273 个文件 / 22,234,796 字节，`scaffold.py` 整目录拷入新站；源代码来自仓库根 `oink-1.3.2/` 目录，排除 `.git/`，逐文件校验一致）
- 判据脚本：`replicate-doc-site/scripts/` 下十个工具，`verify_all.py` 是统一入口
- 使用前先跑自证：`python replicate-doc-site/scripts/verify_all.py --selftest`，末行必须是 `SELFTEST_PASS`——判据要先证明会红，它的绿色才算结论。

## 版本口径（本基线锁定）

| 项 | 值 |
|----|----|
| 主题 | OINK **v1.3.2**（2026-10-18 发布，见主题 `CHANGELOG.md`） |
| Hugo | Extended **≥ 0.166.0**（`hugo.yaml` `module.hugoVersion`；严格发布闸门 `--panicOnWarning` 建议用 0.166.0，普通构建 0.168.0 亦实测通过） |
| Go | `go 1.27.0`（`assets/scaffold/go.mod` 指令，与主题 `go.mod` 对齐） |
| 已实测组合 | Hugo v0.168.0 Extended + Go 1.27.2（骨架实测 `Pages 15 / Static files 34 / 0 ERROR`，产物含 `llms.txt`、离线搜索索引与 `_print/`） |

详细的 1.3.2 主题能力清单（callout、数据围栏、mermaid 渲染链、侧边栏、搜索、goldmark 依赖，以及视觉预设/expo 相册/排版增强等 1.2–1.3.2 新增项）见 `replicate-doc-site/references/oink-theme-capabilities.md`，开头附「与 1.0.0 的主要差异」一节。

## 与 1.0.0 副本的差异速览

两份技能的 scripts、fixtures、example-docs、写作规范完全一致；差异集中在：

1. **主题副本**：`assets/theme/oink-main/oink-main/` 各是各的版本（1.0.0 = 1,196 文件；1.3.2 = 1,273 文件，新增 expo/preset/appearance 等）。
2. **scaffold 模板**：`go.mod` 的 require 行与 `go` 指令、`hugo.yaml` 的 `hugoVersion.min`（0.160.1 vs 0.166.0）、`README.md` 的版本表。
3. **references**：`oink-theme-capabilities.md` 按各自主题副本实测重写（1.3.2 版多一节「与 1.0.0 的主要差异」）；`pitfalls.md` 第 19 条的计数举例各自对齐。
4. **SKILL.md**：主题字节数、实测构建数字、Step 4 的 1.3.x 语法提示（filetree `wrap` / `.td-table--wide` / expo）只在 1.3.2 版有。

### 「新主题」辨析：换了外观体系，没换主题

1.3.2 并没有更换主题——`github.com/pgsty/oink` 是同一个 Hugo 主题（module 路径、29 个 shortcode、18 个 render hook、11 种 callout 逐文件核对全部不变），带来的是**新的「视觉主题/外观」体系与一种内容外壳**：

| 版本 | 带来什么 | 性质 |
|------|---------|------|
| **1.2.0** | **视觉预设体系**：`paper`（暖纸面，**新默认**）、`slate`（= 1.0.0/1.1 的旧技术风）、`ink`（黑白红）、`terminal`（等宽琥珀）四种外观；读者可在 Appearance 菜单自选（`preset_menu`）；本地 IBM Plex Sans 字体 | 观感层面的「新主题」 |
| **1.3.0** | **Expo 图片相册**：第 5 种阅读外壳 `type: expo`（shell_types 从 4 种变 5 种），页面 bundle 出图墙/卡片/无缝布局 + 原图查看器 | 新内容形态，不是外观 |
| **1.3.1** | 可读性修复：Markmap 明暗文字、`.td-table--wide` 宽表、filetree `wrap` | 修复，不是新主题 |
| **1.3.2** | 撤销 1.3.1 的 Dart Sass 强依赖，恢复纯 LibSass 构建 | 构建，不是新主题 |

对应的新增文件：`_presets.scss`、`_experimental-presets.scss`、`appearance.js`、`appearance-menu.html`、`preset-config.html`、10 个 IBM Plex Sans woff2 字体，以及整套 `layouts/expo/` + `expo.js`。

**升级最容易被忽略的一条是默认观感变了**：1.3.2 的主题默认 `preset: paper`，而 1.0.0 时代的外观现在叫 `slate`——同样跑 `hugo server`，两份技能搭出来的站默认不是一个样子。新站要保持 1.0.0 的观感，在 `hugo.yaml` 加：

```yaml
params:
  ui:
    preset: slate      # 1.0.0/1.1 的技术风外观
    # preset_menu: [paper, slate]   # 可选：让读者自己切换
```

外观支持**页面上一键切换**：`preset_menu` 开启后读者可在导航栏/页脚的 Appearance 面板即时切换视觉预设（明暗切换则由 `dark_mode: true` 单独开启，骨架已默认开），选择写入 localStorage 跨页记住、首帧前应用无闪烁；面板是配置门控的，`preset_menu: false`（主题默认）且未开 `dark_mode` 时整个按钮不渲染。`preset_menu: [paper, slate, ink, terminal]` 全开放（列表必须含站点默认 `preset`）。机制细节见 `references/oink-theme-capabilities.md` 第 8 节「外观一键切换」。

本基线已落好：`assets/scaffold/hugo.yaml` 的 `ui:` 段带 `preset: slate` / `preset_menu` 注释项（默认不启用、走 Paper），`references/oink-theme-capabilities.md` 开头「与 1.0.0 的主要差异」一节写明四种预设与 Expo 相册用法。

上游 OINK 的完整变更史见 `replicate-doc-site/assets/theme/oink-main/oink-main/CHANGELOG.md`（1.1.0 界面目录与导航修复、1.2.0 视觉预设、1.3.0 Expo 相册、1.3.1 可读性修复、1.3.2 恢复纯 LibSass 构建）。
