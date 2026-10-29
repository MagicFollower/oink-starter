---
title: 换盘作业相册
description: 一次热插拔换盘作业的分步记录（此处以模拟图顶替）。
date: 2026-10-20
type: expo
expo:
  images: images/*
  mode: seamless
  size: 220
---

相册内 5 张图放在 bundle 的 `images/` 下，由 front matter 的 `expo.images` 选中；
`expo.mode: seamless`、`expo.size: 220` 覆盖站点默认。

| 图 | 尺寸 | 说明 |
|----|------|------|
| dr-step1-pull | 1400 × 800 | (60, 100, 130) |
| dr-step2-tray | 1000 × 1000 | (44, 110, 100) |
| dr-step3-label | 800 × 1100 | (88, 72, 140) |
| dr-step4-insert | 1400 × 900 | (150, 104, 46) |
| dr-step5-rebuild | 1100 × 760 | (112, 58, 74) |

本页所有图片均为**模拟图**：由 `scripts/make-placeholders.py` 生成的带真实宽高色块，用来顶替真实照片，不含任何事实陈述。

