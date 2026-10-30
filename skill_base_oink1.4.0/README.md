# skill_base_oink1.4.0

OINK 1.4.0 基线的技能源目录：`oink-doc-site/` 是技能本体（`SKILL.md` + `assets/` + `references/` + `scripts/`），`示例站点/` 是两套跑通的示例站（`demo-docs-140`、`demo-gallery-140`）。

## 骨架默认行为：表格里的行内代码会折行（不修改oink的基础上自定义样式）

- **位置**：`oink-doc-site/assets/scaffold/assets/scss/_styles_project.scss`。建站时它被拷到站点的 `assets/scss/`，覆盖主题里那份空壳（`oink-main/…/_styles_project.scss`），**主题副本仍逐字节不变**。
- **为什么**：主题给行内 `code` 的是 `overflow-wrap: break-word`——允许视觉折行，但**不把断点计入 min-content**。于是一条长路径会让那一列索要整条路径的宽度，邻列被压成「一字一行」，整表还横向溢出。
- **规则**：`th, td { min-width: 4.5em; overflow-wrap: anywhere }` + `code { overflow-wrap: anywhere; word-break: break-word }`；窄屏（≤575.98px）下限降到 `3.75em`。
- **实测**（1500 视口，4 列表内放 76 字符路径）：骨架默认 `[87, 539, 87, 88]`、表宽 801、溢出 0；把该规则临时禁掉立刻回到 `[44, 675, 44, 44]`、溢出 6。
- **例外**：某张表希望代码保持一行、改为横向滚动，用主题自带的 `{#id .wide}` 标记（列上限 `40ch`，与这条规则互不干扰）。
- **自证**：`scripts/scaffold.py --selftest` 的 `scaffold_ok` 已把该文件纳入检查，缺件即 `SELFTEST_INVALID`。
