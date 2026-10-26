# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。三条硬规矩：**每条命令必须本机跑过并把真实输出原样贴进「实测输出」**；跑不了或没跑的显式写「未验证」+ 原因；不许出现想象中的命令与想象中的输出。环境数字（耗时/体积/版本）标清口径（哪一档、是否 minify、是否首次）。

## 一、前置要求

| 工具 | 版本 | 本机路径 | 为什么必须是它 |
|------|------|---------|----------------|
| Hugo | 【待填：hugo version 实测】 | 【待填】 | 主题用 SCSS，标准版编不了；需要 Extended ≥ 0.166.0 |
| Go | 【待填：go version 实测】 | 【待填】 | 与 `go.mod` 的 `go` 指令对齐，否则触发工具链下载 |

```
【待填：hugo version 与 go version 的真实输出】
```

环境变量硬要求：`GOTOOLCHAIN=local`、`GOPROXY=off`。不设的后果【待填：实测或引用上游问题记录】。

## 二、项目启动（首次构建）

### 双击启动（Windows）

项目根目录的 `run.cmd` 供双击使用。它会切到脚本所在目录、设置 `GOTOOLCHAIN=local` 与 `GOPROXY=off`、优先使用 `HUGO_EXE`（未设置时用 `where hugo`），然后在 `127.0.0.1:8768` 启动 Hugo server 并自动打开浏览器。

实测输出【待填：双击或 `cmd /c run.cmd` 的控制台输出，至少包含 Project / URL / Hugo 版本 / Built in】。

端口被占用时，先在同一个命令行窗口执行 `set PORT=9000`，再运行 `run.cmd`；Hugo 不在 PATH 时用 `set "HUGO_EXE=<hugo.exe 的完整路径>"`。脚本验证时可设 `NO_OPEN=1` 跳过自动打开浏览器。

```
【待填：构建命令】
```

实测输出：

```
【待填：Pages / Static files / Total 原文】
```

判据：0 个 ERROR；WARN 只允许主题侧 `css.Sass: libsass was deprecated` 一条。

## 三、本地调试

`hugo server` 启动方式、重建行为、停止方式【待填：实测输出】；`run.cmd` 在 Windows 上等价于一键执行同一件事，区别是它会打印项目路径、URL 与 Hugo 路径，并自动打开浏览器。路由探针（`curl` 逐个真实状态码）：首页 / `/docs/` / 任一文章页 / 任一图片 / 搜索索引 / 一个不存在的路径（应为 404）。

浏览器实测（写明内核）：顶栏有「文档」入口且能进 `/docs/`；Mermaid 出图数量与 SVG 宽度、表格与 callout 与 💡 小结计数、`scrollWidth > innerWidth` 是否为 false、离线搜索能否命中。

一个坑：搜索面板首次打开显示「正在加载搜索索引……」，索引大时要等状态消失再输查询。

## 四、静态产物与打开方式（对应「打包与启动」）

`hugo --cleanDestinationDir --gc --minify` 的实测输出与产物文件数/字节数（标 minify 与非 minify 两档口径）。`relativeURLs: true` 的实证：深层页面的搜索索引属性会自动补 `../../`，整目录挂到任意子路径都能找到资源。

**双击 `public/index.html` 的实际边界**：页面能打开、文字可读，但 OINK 产物的 CSS/JS 带 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，浏览器会按 CORS 拦截；结果是页面无样式、Mermaid 不渲染、离线搜索 fetch 失败。完整浏览必须走 HTTP：

```bash
python -m http.server 8766 --directory public
# 浏览器打开 http://127.0.0.1:8766/
```

`file://` 只适合快速看纯文字，不要把「双击可用」写成验收结论。

## 五、改站点标题与首页文案（对应「修改标题」）

| 要改什么 | 改哪里 | 生效位置 |
|----------|--------|----------|
| 站点名 | `hugo.yaml` 的 `title: &siteTitle` | 标签页、顶栏、页脚 |
| 顶栏「文档」入口 | `hugo.yaml` 的 `menus.main`（`identifier: docs`、`pageRef: /docs`） | 首页、文档总览和文章页的顶栏；由 `plan_site.py` 生成，重跑计划会保留 |
| 首页大标题/导语/按钮 | `data/home/zh.yaml` 的 `hero` | 首页 |
| 首页卡片 / CTA | 同文件 `cards.items` / `cta` | 首页 |
| 文档总览卡片 | `content/docs/_index.md` 链接列表 + `{.cards}` | `/docs/` |
| 侧边栏下拉卡片文字 | 各一级分类 `_index.md` 的 `linkTitle`/`description`/`icon` | 侧边栏 |

常见半改：只改 `hugo.yaml` 不改 `data/home/zh.yaml`。站点名过长时先在 1280px 宽度看侧边栏品牌是否折行；`ZooKeeper 中文文档` 这类长度可能把最后一个字挤到第二行，必要时缩短或调整品牌字号。

## 六、改图标与配图（对应「修改图标」）

站点 logo、favicon、分类 FontAwesome 图标、`static/images/` 配图与 URL 编码规则【逐项写清路径与生效位置】。配图引用不存在时审计脚本报 `BROKEN_IMAGE`。

## 七、发布与分发

发布档命令、必须随产物分发的文件（离线搜索索引、`llms.txt`、`_print/`、`third_party/mermaid/`、字体与图标）。子路径部署：`relativeURLs: true` 让浏览和资源不用改 `baseURL`，但 canonical、RSS、`sitemap.xml`、`llms.txt` 里的绝对链接仍取 `baseURL`，上线前必须改成真实域名。未做真实部署就写「未验证」+ 原因。

## 八、交付判据与未验证项

| 脚本 | 判据 | 本轮实测 |
|------|------|----------|
| `verify_site.py` | 全站统一验收（构建/结构/链接/预设/顶栏） | 【待填：真实输出行】 |
| `audit_content.py` | 结构、front matter、文体门槛 | 【待填：真实输出行】 |
| `check_links.py` | 以 `public/` 为判据解析站内链接 | 【待填】 |
| `validate_mermaid.py` | 主题自带 mermaid 真解析全部图块 | 【待填】 |

判据自证：`verify_site.py --selftest` 必须 `SELFTEST_PASS`；空骨架的审计必须报出成片问题，否则说明判据没咬住。

## 未验证项汇总

| 项 | 状态 | 原因 |
|----|------|------|
| 【待填：逐条列全】 | 未验证 | 【缺工具/缺权限/离线/无目标环境】 |
