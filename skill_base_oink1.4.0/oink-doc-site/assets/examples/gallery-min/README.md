# gallery-min —— 图库最小参考示例

技能内最小的「gallery 索引 + Expo 相册」内容包：12 条目博客 + 2 个相册 + 图片生成器。
**不含二进制图**：23 张模拟图由 `scripts/make-placeholders.py` 现场生成（纯标准库、零网络），装进站点后总共约 1.4 MB。

## 怎么变成可构建站点

```bash
python <技能目录>/scripts/scaffold.py --out <站点目录>
python <技能目录>/scripts/use_example.py --example gallery-min --site <站点目录>
cd <站点目录> && hugo --cleanDestinationDir
python <技能目录>/scripts/verify_site.py --site . --plan site.plan.json --mode skeleton --hugo hugo
```

`use_example.py` 会复制计划与正文、跑图片生成器、再跑 `plan_site.py`。

## 它演示什么

| 部件 | 演示点 |
|---|---|
| `content/blog/**` | 1.4.0 的 `blog_index: gallery` 索引：12 条目、封面按真实比例铺格；`blog_index_toggle: true` 让读者在 list/cards/table/gallery 四态间切换 |
| `content/albums/**` | Expo 相册（`type: expo` **写在相册页自己身上**，只写 section 时构建零告警但不出图）；图片放 bundle 的 `images/`，由页级 `expo.images/mode/size` 选中 |
| `site.plan.json` | `site.menu` 给 `/blog/` 与 `/albums/` 配顶栏入口（不配就"内容加了、主页没入口"），`home` 按钮与 CTA 直接指向这两个区 |
| `scripts/make-placeholders.py` | 图片按尺寸表生成、宽高写进 PNG 头；改标题或尺寸后重跑一次即可 |
| `doc/内容来源.md` | 两种内容模型的契约、重编码（长边 >960 转 webp）、偏好存储键的登记方式 |

## 已知边界

- 正文验证停在骨架挡（`--mode skeleton`）：交付主体是图库，docs 侧那篇只讲构成与核对命令。
- 浏览器侧交互（三种排布的实际铺格、尺寸滑块、原图查看器手势、无 JS 降级、390px）未验证。
