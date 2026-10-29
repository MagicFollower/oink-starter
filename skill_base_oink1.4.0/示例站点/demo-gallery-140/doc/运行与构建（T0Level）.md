# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。下面每条命令都在本机跑过，输出原样贴在「实测输出」里；没跑的显式写「未验证」并给原因。

环境口径：Hugo v0.168.0 Extended + Go 1.27.3，Windows 本机，非首次构建。主题基线：OINK v1.4.0。本站是**图库示例**，正文验证停在骨架挡（`--mode skeleton`），原因见第六节。

## 一、前置要求

| 工具 | 本机路径 | 为什么必须是它 |
|------|---------|----------------|
| Hugo | `C:\Users\webtu\tools\hugo\hugo.exe`（`D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe` 同版本） | 主题用 SCSS；OINK 1.4.0 要求 Extended ≥ 0.168.0 |
| Go | `C:\Users\webtu\tools\go1.27.3\go\bin\go.exe` | 必须 ≥ 1.27.3：本站 `go.mod` 与被 `replace` 的主题 `go.mod` 取最大值 |

裸敲 `hugo server` 会失败：本机 PATH 里排第一的 go 是 `C:\Program Files\Go\bin`（1.27.2），低于下界时 Go 会去 `proxy.golang.org` 自助下载工具链并超时。`run.cmd` 按 `GO_BIN → GO_FALLBACK → where go` 取到 1.27.3，所以走脚本没问题。

## 二、再生成图片资产

```bash
python scripts/make-placeholders.py .
```

实测输出：

```text
generated_files=27 png=23
png_total_bytes=1381593
```

一次生成 23 张 PNG（12 张 gallery 封面 + 11 张相册图）与 16 个 md。封面尺寸跨度刻意做大：1600×900、1400×700、700×700、640×1024、1100×1500 等，用来把排布的边界情况撑出来。

纯标准库（`struct` + `zlib`），零网络。改尺寸就改脚本顶部的表，重跑一次；不要手改 PNG。

## 三、构建

```bash
hugo --cleanDestinationDir
```

实测输出（统计段）：

```text
WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass
 Pages            │ 82
 Static files     │ 34
Total in 1514 ms
```

除 libsass 这一条外没有其他 WARN——这条要单独看：Expo 的 `type` 写错位置时构建也是零告警，但相册不出图（见第四节）。

判据：0 个 ERROR。不要加 `--panicOnWarning`（1.4.0 主题契约明确禁止）。

## 四、gallery 是否真的生效（产物层）

```bash
grep -ac 'data-td-blog-gallery' public/blog/index.html
grep -ao 'data-td-mode="[a-z]*"' public/blog/index.html | head -1
grep -ao 'data-td-size="[0-9]*"' public/blog/index.html | head -1
grep -ao 'data-gallery-item' public/blog/index.html | wc -l
grep -ao '<img [^>]*width="[0-9]*" height="[0-9]*"' public/blog/index.html | wc -l
find public/js -name 'blog-gallery*' | wc -l
find resources -name '*.webp' | wc -l
```

实测读数：**1、`data-td-mode="wall"`、`data-td-size="240"`、12**；形态切换工具条产出 1 个 `data-td-blog-forms` + 4 个 `data-td-blog-form`。

其中 8 个带宽高的 `<img>` = 6 张封面 + 2 个站点 logo；6 张封面里有 5 张长边超 960 被主题重编码成 webp，只有 800×800 那张保留原文件名。缺图占位（`is-missing`）计数为 0。

## 四之二、Expo 相册是否真的出图

`type: expo` 必须写在**相册页**上。只在 `content/albums/_index.md` 写时，子页的 `.Type` 仍取 section 名 `albums`，走默认模板——构建零错误零告警，相册页一张图都不出。核对：

```bash
for a in rack-inspection disk-replacement; do
  f="public/albums/$a/index.html"
  printf "%-18s 图块=%s img=%s %s %s
" "$a" \
    "$(grep -c 'data-td-expo-item' "$f")" "$(grep -o '<img ' "$f" | wc -l)" \
    "$(grep -o 'data-td-expo-mode="[a-z]*"' "$f" | head -1)" \
    "$(grep -o 'data-td-expo-size="[0-9]*"' "$f" | head -1)"
done
```

实测：

```text
rack-inspection    图块=6 img=9 data-td-expo-mode="cards" data-td-expo-size="260"
disk-replacement   图块=5 img=8 data-td-expo-mode="seamless" data-td-expo-size="220"
```

## 五、本地预览

```bash
run.cmd
```

实测输出（`NO_OPEN=1 NO_PAUSE=1`）：

```text
 Project : C:\Users\webtu\Desktop\silo文档站\示例站点\demo-gallery-140
 Hugo    : D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe
 Go      : C:\Users\webtu\tools\go1.27.3\go\bin\go.exe
 Note    : Go 1.27.3 or newer is required by go.mod.
Starting Hugo server without opening a browser...
 Pages            │ 45
Built in 649 ms
```

实测逐条（`hugo` 构建后 `hugo server`）：

| 路径 | HTTP | 备注 |
|---|---|---|
| `/` | 200 | 标题「OINK 1.4.0 图库示例」，顶栏三条入口「文档 / 图集 / 相册」 |
| `/blog/` | 200 | gallery 索引，`data-gallery-item` 12 个 |
| `/albums/` | 200 | Expo 相册列表 |
| `/albums/rack-inspection/` | 200 | 6 图块相册页 |
| `/docs/` | 200 | 说明文档 |

页面里 `./scss/main.css` 与 `./icons/logo.svg` 均 200。**顶栏入口来自 `site.plan.json` 的 `site.menu`**：OINK 只渲染 `menus.main`，不写这条的话 `/blog/` 与 `/albums/` 虽然能构建，导航里却一个入口都没有（构建零告警），读者只能手输地址。

`baseURL` 保持根：本站早期把它写成 `https://docs.example.com/demo-gallery-140/`，于是资源 URL 被烤成 `./demo-gallery-140/scss/main.css`，浏览器解析成双前缀后 CSS 与 logo 全 404（页面本身仍 200）。`check_links` 当时报 `broken=17`，改回根之后 `broken=0`。挂子路径请交给部署目录。

完整功能必须走 HTTP；不要用 `file://` 打开 `public/index.html`，`integrity` + `crossorigin` 会被按 CORS 拦截，只剩无样式文字。

## 六、验收为什么停在骨架挡

```bash
python <技能目录>/scripts/verify_site.py --site . --plan site.plan.json --mode skeleton \
    --hugo hugo --go-bin "C:\Users\webtu\tools\go1.27.3\go\bin"
```

实测汇总行：

```text
FAIL=0 MANUAL=2 PASS=7 SKIP=1
```

links 行含资源 URL 判据：`check_links` 解析 41 个页面 621 条 `<link>/<script>/<img>`，`broken=0 unmapped=0`。

逐行读数：`plan problems=0`、`scaffold theme_files=1292 placeholders=0 preset=paper run_cmd=ok`、`build Pages=45 Static files=34 ERROR=0`、`preset data-td-preset=paper menu=list:4`、`nav 顶栏文档入口存在`、`audit articles=1 expected=1 problems=0 mode=skeleton`、`links links_checked=5 broken=0 unmapped=0 home_urls=4`（links 行含资源 URL 判据，本站 22 个页面 290 条资源全部落地）。

本站的交付主体是图库；docs 侧那一篇正文按图库演示的需要写（讲部件、给核对命令），没有扩到成品挡要求的篇幅，因此**不声称 `--mode full` 通过**。要把它升到成品挡，得给每篇正文补足篇幅与结构门槛，并把第五节的未验证项跑完。

## 七、未验证清单

- 三种排布（墙 / 卡片 / 无缝）在浏览器里的实际铺格与跨行对齐。
- 尺寸滑块（160–360，步进 20）的响应与偏好持久化。
- `td-blog-gallery-mode` / `td-blog-gallery-size` 与 Expo 相册偏好是否互不串台（只读了源码）。
- 禁用 JavaScript 与缺图两种降级路径的实际呈现。
- 390 像素窄屏下的横向溢出。

## 八、常见故障

| 现象 | 结论 |
|---|---|
| `go: downloading go1.27.3` 后构建失败 | 命中的 Go 低于下界；换执行的那个 go.exe，改本站 `go.mod` 没用（主题自身那条也参与取下界） |
| 预览根路径 404 | `baseURL` 带子路径，要访问 `/demo-gallery-140/` |
| 索引页看不到 gallery 工具条 | 先确认第四节产物层有 `data-td-blog-gallery`；没有就是 `blog_index` 没生效（检查页面级是否覆盖了站点级） |
| 双击 `public/index.html` 只剩文字 | `file://` 的 CORS 拦截，不是内容坏了；走 HTTP |
