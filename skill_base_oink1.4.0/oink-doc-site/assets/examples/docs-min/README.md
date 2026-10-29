# docs-min —— 文档站最小参考示例

技能内最小的「用满 1.4.0 作者侧标记」的文档站内容包：`site.plan.json` + 两篇成品正文 + 内容来源清单。
不含主题、不含 `public/`、不含图片——那些由 `scaffold.py` 与构建命令负责。

## 怎么变成可构建站点

```bash
python <技能目录>/scripts/scaffold.py --out <站点目录>
python <技能目录>/scripts/use_example.py --example docs-min --site <站点目录>
cd <站点目录> && hugo --cleanDestinationDir
python <技能目录>/scripts/verify_site.py --site . --plan site.plan.json --mode full --hugo hugo
```

`use_example.py` 会复制计划与正文、跑 `plan_site.py`，并打印下一条命令。

## 它演示什么

| 文件 | 演示点 |
|---|---|
| `content/docs/01-tour/排版增强/feature-tour.md` | 表格 `.wide` / `.expand` / 两者叠加（属性行**写在表格之后紧贴**、id 必须是 ASCII）、`cards variant="list"`、`steps variant="compact"`（条目是一个三级标题）、`.td-code-command` 命令条、以及每件的写错退路 |
| `content/docs/02-diagrams/渲染口径/diagrams.md` | Mermaid 与 PlantUML 的开关位置、懒渲染三态（源码态/成功/失败）的分辨、离线解析台与页面判据的分工；PlantUML 需在计划里开 `site.params.plantuml.enable` |
| `site.plan.json` | 2 分类 × 1 板块 × 1 篇的最小计划；`site.params` 承载 `plantuml.enable`（重跑计划不会冲掉） |
| `doc/内容来源.md` | 每条技术事实对应到主题源码行/上游 CHANGELOG 的登记方式 |

两篇正文都达到 `--mode full` 的结构门槛（≥260 行、3 个新人小结、mermaid、表格、带语言代码块、要点总结）。

## 已知边界

- 不含图片与 expo 内容；需要图库形态看 `gallery-min`。
- 浏览器侧观感（抽屉开合还原、图表缩放/下载、390px）未在示例包里验证，验收时按 SKILL Step 5 的走查清单做。
