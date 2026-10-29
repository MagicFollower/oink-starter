---
title: "这个图库站由哪些部件组成"
description: "说明图库站的两个入口——gallery 索引与 Expo 相册——各自的开关位置、图片契约、再生成命令，以及本轮量到了什么。"
weight: 1
---

这是一个可以直接改的图库站：12 条目走 OINK 1.4.0 新增的 `gallery` 索引形态，另加 2 个 Expo 相册页走「一个相册多张图」的形态。两者共用同一批**模拟图**（脚本生成的带真实宽高色块），所以整站可以离线重建。

本页只讲三件事：部件在哪、图片必须满足什么、以及哪些结论是量出来的、哪些还没验。

## 为什么要分两块，而不是只用一种图

| 需求 | 适合 | 不适合 |
|---|---|---|
| 一张图配一段说明、要能按时间/标签翻找、要点进详情页 | gallery 索引（条目 + 封面） | 只想一次看完整批照片 |
| 一次作业/一次巡检拍的一组照片，要连着翻、要看原图 | Expo 相册（bundle 内多图） | 需要每条目独立 URL 与标签 |

两块的区别不是样式差异，而是**内容模型差异**：gallery 排的是「页面」，Expo 排的是「一个页面里的图片集合」。所以本站两块都留了一份，方便照着改。

```bash
python scripts/make-placeholders.py .
```

这条命令重建全部 23 张 PNG 与 16 个 md（含两个 `_index.md`），纯标准库、零网络。实测输出末两行：

```text
generated_files=27 png=23
png_total_bytes=1381593
```

## 部件一：gallery 索引（12 条目）

每个条目是一个 leaf bundle：`content/blog/<slug>/index.md` + `featured.png`。封面解析优先级是 `**featured*` → `*feature*` → `{*cover*,*thumbnail*}` → front matter `images`，本站命中第一条。

形态开关分两层，**页面级覆盖站点级**：

| 键 | 本站取值 | 位置 |
|---|---|---|
| `blog_index` | `gallery` | `content/blog/_index.md` 的 front matter |
| `blog_index_toggle` | `true` | 同上；读者可在四种形态间切换 |
| `blog_gallery.mode` / `.size` | `wall` / 240 | 同上；`size` 允许 160–360 |

`blog_index_toggle` 的取值顺序在主题里是「先看页面参数，再退到 `params.ui.blog_index_toggle`」（`layouts/_partials/shell/blog-index-toggle.html` 用 `ui-param.html` 做这件事），所以写在 section 的 front matter 上就够，不必动站点配置——这也避开了「手改 `hugo.yaml` 会被下一次重跑计划冲掉」那个坑。

> 💡 新人小结：gallery 与 Expo 的偏好是两套存储键，读者在索引页换的排布不会影响相册页，反之也一样。

## 部件二：Expo 相册（2 个）

相册节 `content/albums/_index.md` 用 `type: expo` 换阅读外壳；每个相册是一个 bundle，图片放在 bundle 的 `images/` 下，由 front matter 选中：

```yaml
expo:
  images: images/*
  mode: cards
  size: 260
```

两个相册刻意用了不同排布：机柜巡检是 `cards`/260，换盘作业是 `seamless`/220，方便直接对比。主题注释写明 `images/*` 是 bundle 资源通配、**不做远程取图**，所以图片必须在仓库里。

**一个不写就会静默失效的点**：`type: expo` 必须写在**相册页自己**的 front matter 上。Hugo 的页面 `.Type` 默认取所在 section 名，只在 `content/albums/_index.md` 写 `type: expo` 时，section 列表页走了 expo 外壳、子页却仍按默认模板渲染——构建 0 错误 0 告警，相册页一张图都不出。本站实测补上页级 `type` 后：机柜相册 `data-td-expo-item` = 6、`<img>` = 9、`mode=cards`、`size=260`；换盘相册 = 5、8、`seamless`、220。核对就数这两个属性，别只看构建返回码。

## 图片必须满足什么

| 要求 | 为什么 | 本站怎么保证 |
|---|---|---|
| 真实宽高写进文件 | 两种排布都按比例铺格，尺寸写进 `<img>` 才能在图到位前算好布局 | 生成器把尺寸写进 PNG 头，另有核对命令 |
| 长边超过 960 会被重编码 | 封面按 `960x960 webp` 出预览，比例仍按原图 | 别把文件名当证据，去 `resources/` 看产物 |
| 每格视觉可区分 | 排布错位与「图没加载」在截图上很像 | 色块按频率分带，每格不同 |

核对命令与本轮实测：

```bash
python - <<'PY'
import struct, glob
n = 0
for p in sorted(glob.glob("content/**/featured.png", recursive=True)) + sorted(glob.glob("content/albums/*/images/*.png", recursive=True)):
    b = open(p, "rb").read()
    w, h = struct.unpack(">II", b[16:24])
    n += 1
print("png_checked=%d" % n)
PY
```

## 这一轮量到的

| 项 | 读数 |
|---|---|
| 生成 | 23 张 PNG、16 个 md，PNG 合计 1,381,593 字节 |
| 构建 | `Pages 82 / Static files 34 / Total in 1514 ms`，0 个 ERROR，除 libsass 外无 WARN |
| gallery 索引 | 条目格数 12，`data-td-mode="wall"`、`data-td-size="240"` |
| 形态切换工具条 | 1 个 `data-td-blog-forms` + 4 个 `data-td-blog-form`（list/cards/table/gallery） |
| Expo 相册 | 机柜 6 图块 / 9 `<img>` / `cards` 260；换盘 5 图块 / 8 `<img>` / `seamless` 220 |
| 封面重编码 | `resources/` 下 26 个 webp（长边超 960 的被 Fit 成 960×960，比例不变） |
| 资源判据 | `check_links` 解析 41 个页面 621 条资源，`broken=0 unmapped=0` |
| 统一验收 | `verify --mode skeleton` → `FAIL=0 MANUAL=2 PASS=7 SKIP=1` |

## 未验证清单

- 三种 gallery 排布与 Expo 的 wall/cards/seamless 在浏览器里的实际铺格与跨行对齐。
- 尺寸滑块、原图查看器手势、键盘流、记忆布局（本技能对 Expo 的浏览器行为历来未实测）。
- 无 JS 与缺图两条降级路径的实际呈现。
- 390 像素窄屏的横向溢出。

## 要点总结

- 图库站由 gallery 索引（12 条目，一页一图）与 Expo 相册（2 页，一页多图）两块组成，内容模型不同，不是样式不同。
- 开关全部写在 section 的 front matter 上：`blog_index`、`blog_index_toggle`、`blog_gallery`，以及相册页的 `expo`；这样重跑 `plan_site.py` 不会冲掉。
- 图片一律由脚本生成、带真实宽高，核对要看 PNG 头而不是产物文件名——长边超 960 的封面会被重编码成 webp。
- 本轮只完成构建与产物层核对，所有浏览器侧交互仍记为未验证。
