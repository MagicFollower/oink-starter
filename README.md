# OINK Starter

用 [OINK](https://oink.pgsty.com/) 和 Hugo 给开源项目搭文档站的最小可用骨架：自带英文、简体中文、法文三套首页，Blog、Docs、Book 三类内容，以及一条严格的生产构建命令。

仓库里不含任何真实项目的品牌、文档、分析账号、评论仓库或回归套件。Google Analytics 与 Giscus 的配置整块保持注释状态，你不主动启用就一段都不会加载。

> 本仓库是 [pgsty/oink-starter](https://github.com/pgsty/oink-starter) 的本地分叉，与上游有两处差异：部署工作流已删除（见「部署」一节），仓库内另附一份文档站复刻技能（见「附带技能」一节）。上游英文说明保留在 `README_en.md`。

## 三步跑起来

从你自己的仓库地址开始：

```bash
git clone https://github.com/YOU/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
hugo server
```

打开 <http://localhost:1313/>。首次构建会联网拉取钉住的 OINK Hugo Module（`go.mod` 里是 `github.com/pgsty/oink v1.0.0`）。

构建需要 Git、Go 1.27 及以上（`go.mod` 声明 `go 1.27.0`）、Hugo Extended。Hugo 的硬下限写在 `hugo.yaml` 末尾的 `hugoVersion`（`extended: true`、`min: 0.160.1`），上游那两条工作流当年钉的是 0.165.0。不需要 Node.js 与 npm，仓库里没有 `package.json`。

## 改成你自己的

默认站点不改任何东西也能构建。真要做自己的项目，先只动这三处：

1. `hugo.yaml` 顶部的 `Project Name` 与 `https://example.org/`。
2. 替换 `data/home/` 下的 `en.yaml`、`zh.yaml`、`fr.yaml` 三份精简首页数据。
3. 重写或删除 `content/` 下的示例页。

站名只用了同一个 YAML 锚点（`title: &siteTitle`，三种语言各自 `title: *siteTitle`），改一次三语同变。导航跟着各栏目的译文 `_index` 页面走，重命名栏目不用另外维护第二份菜单树。`assets/icons/logo.svg` 与 `static/favicon.svg` 只在手上真有品牌素材时才替换。

常用可选项已经在 `hugo.yaml` 里分组注释好：仓库链接（`github_repo`、`github_branch`）、Giscus（`comments`）、Google Analytics（`services.googleAnalytics`）、主题色（`ui.theme_color`）、字体（`ui.typography`）、图片缩放（`ui.image_zoom`）、分享（`ui.share`）、页脚反馈（`ui.feedback`）、logo 与 wordmark、页面宽度（`page_width`）。要真的运营那个第三方服务时，才把对应整块的注释去掉。

## 内容地图

```text
content/
├── blog/
│   ├── post/          文章
│   ├── design/        设计说明与决策
│   └── release/       发布公告
├── docs/
│   ├── introduction/
│   ├── get-started/
│   ├── tutorial/
│   └── reference/
└── book/              讲本模板自己的一本小书
```

英文正文以 `.md` 结尾，中文与法文同名并排，后缀是 `.zh.md` 与 `.fr.md`。译文与原文放在一起，显式标题 ID（`## Tools {#tools}` 这种写法）要逐条对齐。

## 语言配置档

根目录 `hugo.yaml` 同时启用英文、中文、法文。另备两份可直接覆盖的配置档：

```bash
cp examples/hugo.single.yaml hugo.yaml     # 只留英文（disableLanguages: [zh, fr]）
cp examples/hugo.bilingual.yaml hugo.yaml  # 英文 + 中文（disableLanguages: [fr]）
```

两份都保留未启用语言的声明，Hugo 因此仍认得对应后缀并安全忽略其内容。下次换配置档前，先用 Git 把三语配置取回来。

## 构建与验收

写作时预览：

```bash
hugo server
```

本地跑一遍发布闸门（有告警即失败）：

```bash
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

产物 `public/` 以及 `resources/`、`.hugo_cache/`、`.hugo_build.lock` 都已在 `.gitignore` 里，不要提交。

## 部署

上游的 `.github/workflows/github-pages.yaml` 与 `.github/workflows/cloudflare-pages.yaml` 已在本仓库删除（提交 `ac422c2 移除workflows`），所以现在没有推送即部署的流水线。两条路：

手动部署：先跑上面那条严格构建命令，再把生成的 `public/` 交出去——GitHub Pages 把来源设为分支（例如把 `public/` 推到 `gh-pages`）后由 Pages 直接发布，Cloudflare Pages 用 Direct Upload 上传这个目录。

接回工作流：从历史里取回，自己核对后再提交。

```bash
mkdir -p .github/workflows
git show 'ac422c2~1:.github/workflows/github-pages.yaml' > .github/workflows/github-pages.yaml
git show 'ac422c2~1:.github/workflows/cloudflare-pages.yaml' > .github/workflows/cloudflare-pages.yaml
```

取回前需要知道的内容：两份文件的 `HUGO_VERSION` 都是 0.165.0，都用 `actions/setup-go@v7` 按 `go.mod` 装 Go、先 `go mod download github.com/pgsty/oink`、再跑同一条带 `--panicOnWarning` 的构建。GitHub Pages 那份先在 **Settings → Pages** 里把来源选成 **GitHub Actions**，构建时把 `--baseURL` 覆盖成 `actions/configure-pages` 算出的项目子路径。Cloudflare 那份走 Direct Upload（`cloudflare/wrangler-action@v4`），需要 `CLOUDFLARE_ACCOUNT_ID` 与 `CLOUDFLARE_API_TOKEN` 两个 secret（token 权限为 Account → Cloudflare Pages → Edit）；项目名默认取仓库名，可用仓库变量 `CLOUDFLARE_PROJECT_NAME` 覆盖；canonical 地址默认 `https://<project>.pages.dev/`，挂自定义域名时设 `CLOUDFLARE_SITE_URL`；只有设了 `CLOUDFLARE_PAGES_ENABLED=true` 才每次推送 `main` 自动部署，否则手动触发。同一个 Pages 项目要么用 Cloudflare 的 Git 集成、要么用这份 Direct Upload 工作流，不要两个一起。

## 附带技能

`skills--LOOK_ME/replicate-doc-site/` 是本仓库自加的一份技能（上游没有），把既有文档站（Docusaurus、VitePress、GitBook、自站）整站复刻成本地 Hugo + OINK 站点。`SKILL.md` 是流程主文；`scripts/` 下是 `scaffold.py`、`check_coverage.py`、`audit_structure.py`、`matrix_check.py`、`verify_all.py` 等判据脚本；`references/` 是写作规范、覆盖矩阵口径与主题能力清单；`assets/` 带骨架模板、六份体裁样章、会自己失败的夹具，以及一份离线主题副本。用之前先跑 `python scripts/verify_all.py --selftest`——判据要先证明会红，它的绿色才算结论。

## 什么叫做完了

本地构建成功、改动已提交、分支已推送、工作流转绿、公网渲染正确，是五道各自独立的闸门。部署后要逐个打开 `/`、`/zh/`、`/fr/`，再从 Blog、Docs、Book 各抽一页，桌面和移动端各看一遍。

## 许可

MIT。采用本模板时，把 `LICENSE` 的通用版权声明（现为 `The contributors`）与 `hugo.yaml` 里的 `copyright.authors` 换成你自己的。
