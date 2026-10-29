# OINK 1.4.0 图库示例 — 文档站操作规范

本项目是基于 Hugo + OINK v1.4.0 的中文文档站，主题与运行时全部本地化，构建过程不联网。本文件说明目录约定、写作门槛与验收命令，读完即可接手维护。

## 一、项目结构

```text
OINK 1.4.0 图库示例/
├── content/_index.md              # 首页
├── content/docs/                  # 文档主区域
│   ├── _index.md                  # 文档总览（卡片导航）
│   └── NN-分类/板块/文章.md
├── static/images/                 # 配图（正文用 /images/xxx.png）
├── data/home/zh.yaml              # 首页 hero / 卡片 / CTA
├── hugo.yaml                      # 站点唯一配置
├── go.mod                         # 主题走 replace 本地化
├── run.cmd                        # Windows 双击启动本地预览
├── oink-main/oink-main/           # OINK 主题（勿修改）
├── doc/                           # 编写规范、运行与构建
└── site.plan.json                 # 导航计划（生成导航的源数据）
```

## 二、内容分类（共 1 类 / 1 篇）

| 目录 | 分类 | 板块 |
|------|------|------|
| `01-gallery/` | 图库说明 | 构成 |

新增分类或文章：改 `site.plan.json`，再跑 `plan_site.py --site . --plan site.plan.json`。不要只手建目录，目录与 `_index.md` 必须成对。

顶栏「文档」tab 由生成器写入 `hugo.yaml` 的 `menus.main`（`identifier: docs`、`pageRef: /docs`）。OINK 1.4.0 的顶栏只渲染这个配置，主题不会自动挂入口；重跑计划会保留该键。

## 三、命名与 Front Matter

| 层级 | 命名 | 示例 |
|------|------|------|
| 一级分类目录 | 小写字母/数字/短横线 | `01-overview/` |
| 二级板块目录 | 中文或英文，不含空白与斜杠 | `核心概念/` |
| 文章文件 | 中文或英文，不含空白与斜杠 | `一致性协议.md` |

文章三字段缺一不可；`weight` 在同目录内 1..N 连续不重复：

```yaml
---
title: 文章标题
description: 一句话说明本文解决什么问题（至少 20 字，会进侧边栏卡片与 SEO）。
weight: 1
---
```

一级分类 `_index.md` 带 `type: docs`、`icon`、`weight`、`sidebar_root_for: self`、`sidebar_root_link_self: true` 与 `cascade`；板块 `_index.md` 只需 `title`/`linkTitle`/`description`/`weight`。这些文件由 `plan_site.py` 生成，手改后重跑计划会被覆盖。

## 四、写作与事实来源

正文按 `doc/技术文档编写规范.md` 写。机器门槛（`audit_content.py --mode full`）：

- 首个真实 H2 以「为什么」开头；
- 全文 ≥ 260 行、≥ 3 个「💡 新人小结」、≥ 1 个 mermaid、≥ 2 组表格、≥ 1 个带语言标注的代码块；
- 必须有「要点总结」；description ≥ 20 字；
- 禁止「限于篇幅 / 此处从略 / 自行查阅 / 待补充 / TODO / 感兴趣请 / 众所周知 / 不言而喻」；
- 禁止用 `┌┐└┘├┤┬┴┼` 画图，结构化图用 mermaid。

**技术事实只能来自可核验来源**：用户提供的材料、官方文档/仓库、真实命令输出。具体默认值、版本号、限制数值、异常语义查不到就不写，或明确写「上游未给出」。每批写作在 `doc/内容来源.md` 登记来源，交付时作为 MANUAL 项核对。

## 五、构建与环境

| 工具 | 版本 | 要求 |
|------|------|------|
| Hugo | ≥ 0.168.0 **Extended** | 标准版无法编译 SCSS；主题契约禁止 `--panicOnWarning`，libsass WARN 保持可见即可 |
| Go | ≥ 1.27.3（站点与主题两处 `go.mod` 取最大值） | 版本低于要求时 Go 会自己去 proxy 下载工具链，离线机直接失败；PATH 里有旧 Go 时用 `--go-bin` 指向 1.27.3 的 bin |

```bash
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir          # 构建
run.cmd                             # Windows：双击或命令行启动本地预览
hugo server -D                      # 非 Windows 或手动启动
python -m http.server 8766 --directory public   # 纯静态产物预览
hugo --cleanDestinationDir --gc --minify   # 发布档
```

Windows 的 `run.cmd` 会自动设置离线构建变量、查找 Hugo（找不到时可用 `HUGO_EXE` 指定完整路径）、在 `127.0.0.1:8768` 启动 Hugo server 并打开浏览器；端口冲突时先 `set PORT=9000` 再运行。`NO_OPEN=1` 可跳过自动打开浏览器，适合脚本验证。

离线构建要同时满足：主题副本在 `oink-main/oink-main/`、`go.mod` 的 replace 指向它、被执行的 Go ≥ 1.27.3。Hugo 报 `failed to load modules` 时先查 Go，不是内容错误：`binary with name "go" not found in PATH` 是没装，`go: downloading go1.27.3 …` 是装了但版本低于要求（Go 正试图自己下载新工具链，离线机必然失败）。设 `GOTOOLCHAIN=local` 只是把报错换成 `go.mod requires go >= 1.27.3`，并不会让旧 Go 够用；把实际执行的那个 go.exe 换成 1.27.3 才是解。验收时用 `--go-bin` 显式指向正确的 bin。

**打开方式**：完整功能请走 HTTP（`hugo server` 或上面的 `python -m http.server`）。直接双击 `public/index.html` 只有无样式文字：OINK 产物的 CSS/JS 带 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，会被浏览器 CORS 拦截，Mermaid、离线搜索、Appearance 都不可用。

## 六、约束

1. 不修改 `oink-main/` 主题目录。
2. 正文语言为中文，不做多语言混排；`.md` 即中文正文。
3. 目录与 `_index.md` 成对出现；文章必须有 front matter。
4. 一篇文档只归一个板块；跨板块关联用站内链接，不复制正文。
5. 不把本地临时路径、审计报告措辞写进正文；配图放 `static/images/`，正文用 `/images/...`。
