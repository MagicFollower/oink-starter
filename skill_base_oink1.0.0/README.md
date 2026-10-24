# replicate-doc-site 技能（OINK v1.0.0 基线）

本目录是 `replicate-doc-site` 技能的 **OINK v1.0.0 基线副本**：内置主题、判据脚本、写作规范与自证夹具全部按 OINK 1.0.0 时代的实测事实冻结。复刻目标站点明确要求旧版 OINK 行为时用这一份；新项目请用 `../skill_base_oink1.3.2/`（两份技能结构完全相同，仅主题副本与版本相关事实不同）。

- 技能主体：`replicate-doc-site/SKILL.md`（流程主文，从 Step 0 到验收）
- 主题本体：`replicate-doc-site/assets/theme/oink-main/oink-main/`（OINK v1.0.0，1,196 个文件 / 21,257,008 字节，`scaffold.py` 整目录拷入新站）
- 判据脚本：`replicate-doc-site/scripts/` 下十个工具，`verify_all.py` 是统一入口
- 使用前先跑自证：`python replicate-doc-site/scripts/verify_all.py --selftest`，末行必须是 `SELFTEST_PASS`——判据要先证明会红，它的绿色才算结论。

## 版本口径（本基线锁定）

| 项 | 值 |
|----|----|
| 主题 | OINK **v1.0.0**（`go.mod` require 与主题 `theme.toml`/CHANGELOG 对应 1.0.0 发布线） |
| Hugo | Extended **≥ 0.160.1**（`hugo.yaml` `module.hugoVersion`） |
| Go | `go 1.25.4`（`assets/scaffold/go.mod` 指令；≥1.27 亦兼容） |
| 已实测组合 | Hugo v0.168.0 Extended + Go 1.25.4（历史项目实测跑通） |

详细的 1.0.0 主题能力清单（callout、数据围栏、mermaid 渲染链、侧边栏、搜索、goldmark 依赖）见 `replicate-doc-site/references/oink-theme-capabilities.md`。

## 与 1.3.2 副本的差异速览

两份技能的 scripts、fixtures、example-docs、写作规范完全一致；差异集中在：

1. **主题副本**：`assets/theme/oink-main/oink-main/` 各是各的版本（1.0.0 = 1,196 文件；1.3.2 = 1,273 文件，新增 expo/preset/appearance 等）。
2. **scaffold 模板**：`go.mod` 的 require 行与 `go` 指令、`hugo.yaml` 的 `hugoVersion.min`（0.160.1 vs 0.166.0）、`README.md` 的版本表。
3. **references**：`oink-theme-capabilities.md` 按各自主题副本实测重写（1.3.2 版多一节「与 1.0.0 的主要差异」）；`pitfalls.md` 第 19 条的计数举例各自对齐。
4. **SKILL.md**：主题字节数、实测构建数字、Step 4 的 1.3.x 语法提示（filetree `wrap` / `.td-table--wide` / expo）只在 1.3.2 版有。

上游 OINK 的完整变更史见 `replicate-doc-site/assets/theme/oink-main/oink-main/CHANGELOG.md`（本副本止于 1.0.0 发布线；1.1.0 之后的变更见 `../skill_base_oink1.3.2/` 副本内的同路径文件）。
