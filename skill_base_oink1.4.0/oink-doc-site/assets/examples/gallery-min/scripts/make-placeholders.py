"""demo-gallery-140 的图片与正文生成器（纯标准库，零网络）。

产出两块：
  content/blog/**        —— 12 篇带封面的条目，索引用 1.4.0 的 gallery 形态
  content/albums/**      —— 2 个 Expo 相册页（bundle 内 images/*）

所有图都是**模拟图**：带真实宽高的色块，用来顶替真实照片，不含任何事实陈述。
"""
import os
import struct
import zlib

BLOG = [
    # slug, 宽, 高, 基色, 条纹频率, 标题, 描述, 标签, 日期
    ("object-wall-01", 1200, 800, (36, 78, 128), 7, "对象墙全景", "一次批量写入后各磁盘占用的全景视图。", ["巡检", "对象层"], "2026-09-03"),
    ("object-wall-02", 900, 1200, (44, 96, 146), 5, "对象墙纵列", "同一批数据在纵向分片上的分布，看倾斜。", ["巡检", "对象层"], "2026-09-03"),
    ("tiering-hot-01", 1024, 1024, (30, 112, 96), 8, "热层落盘", "冷热分层切换前，热数据实际落在哪一层。", ["分层"], "2026-09-11"),
    ("tiering-cold-01", 1400, 700, (34, 124, 108), 4, "冷层搬移带", "一次冷层搬移期间的带宽占用曲线。", ["分层", "容量"], "2026-09-11"),
    ("erasure-set-01", 800, 800, (64, 64, 146), 9, "纠删码集合 A", "一个纠删码集合内各分片的占用对照。", ["纠删码"], "2026-09-19"),
    ("erasure-set-02", 1100, 1500, (76, 72, 158), 6, "纠删码集合 B", "第二个集合，用来对照分片是否提前写满。", ["纠删码", "容量"], "2026-09-19"),
    ("replication-lag-01", 1600, 900, (150, 92, 40), 5, "跨站点延迟全景", "同一批对象在两个站点的到齐时间差。", ["复制", "延迟"], "2026-09-26"),
    ("replication-lag-02", 700, 700, (166, 106, 52), 10, "延迟尖峰局部", "一次网络抖动期间的局部延迟放大视图。", ["复制", "延迟"], "2026-09-26"),
    ("quota-01", 1024, 640, (108, 48, 66), 8, "配额触达", "配额从告警到硬拦截之间的拒绝比例。", ["配额"], "2026-10-05"),
    ("lifecycle-01", 640, 1024, (122, 56, 78), 7, "生命周期路径", "规则从匹配、排队到执行完的三段耗时。", ["生命周期"], "2026-10-05"),
    ("gateway-01", 1280, 720, (88, 88, 96), 6, "网关主备切换", "切换瞬间会话保持与请求失败的对照。", ["网关"], "2026-10-14"),
    ("console-01", 960, 1280, (52, 84, 112), 9, "控制台总览", "容量、健康与告警三块面板的排布示意。", ["控制台"], "2026-10-14"),
]

ALBUMS = [
    ("rack-inspection", "机柜巡检相册", "一次例行巡检拍摄的机柜与链路照片集合（此处以模拟图顶替）。", "cards", 260, [
        ("rack-a-front", 1200, 1600, (40, 70, 110), "A 列正面"),
        ("rack-a-cables", 1600, 1000, (56, 92, 128), "A 列走线"),
        ("rack-b-front", 1200, 1200, (48, 84, 96), "B 列正面"),
        ("rack-b-labels", 900, 1350, (72, 66, 120), "B 列标签"),
        ("rack-c-power", 1500, 950, (140, 96, 48), "C 列电源"),
        ("rack-c-empty", 800, 1200, (96, 52, 66), "C 列空位"),
    ]),
    ("disk-replacement", "换盘作业相册", "一次热插拔换盘作业的分步记录（此处以模拟图顶替）。", "seamless", 220, [
        ("dr-step1-pull", 1400, 800, (60, 100, 130), "步 1 抽出"),
        ("dr-step2-tray", 1000, 1000, (44, 110, 100), "步 2 托盘"),
        ("dr-step3-label", 800, 1100, (88, 72, 140), "步 3 标签"),
        ("dr-step4-insert", 1400, 900, (150, 104, 46), "步 4 回插"),
        ("dr-step5-rebuild", 1100, 760, (112, 58, 74), "步 5 重建"),
    ]),
]

NOTICE = "本页所有图片均为**模拟图**：由 `scripts/make-placeholders.py` 生成的带真实宽高色块，用来顶替真实照片，不含任何事实陈述。"


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, w, h, rgb, freq):
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        for x in range(w):
            band = ((x // max(1, w // freq)) + (y // max(1, h // freq))) % 2
            shade = 0.55 + 0.45 * (1 - abs(2 * (x / w) - 1)) * (1 - abs(2 * (y / h) - 1))
            factor = (0.85 if band else 0.45) * shade
            rows += bytes((int(rgb[0] * factor), int(rgb[1] * factor), int(rgb[2] * factor)))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(rows), 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def fm(d):
    lines = ["---"]
    for k, v in d.items():
        if isinstance(v, list):
            lines.append("%s: [%s]" % (k, ", ".join('"%s"' % x for x in v)))
        elif isinstance(v, dict):
            lines.append("%s:" % k)
            for k2, v2 in v.items():
                lines.append("  %s: %s" % (k2, v2))
        else:
            lines.append("%s: %s" % (k, v))
    lines.append("---")
    return "\n".join(lines) + "\n"


def build(root):
    made = []
    blog = os.path.join(root, "content", "blog")
    os.makedirs(blog, exist_ok=True)
    write(os.path.join(blog, "_index.md"), fm({
        "title": "图集", "description": "巡检与作业照片的索引页，用 OINK 1.4.0 新增的 gallery 形态承载。",
        "blog_index": "gallery", "blog_index_toggle": "true",
        "outputs": "[HTML, RSS, print]",
    }) + "\n".join([
        "", "这一节是图库主入口：12 条目，封面按真实比例铺格。",
        "",
        "读者可以在工具条里于 `list` / `cards` / `table` / `gallery` 四种形态之间切换（站点开了 `blog_index_toggle: true`），",
        "也可以在 gallery 下换 `wall` / `cards` / `seamless` 三种排布并拖尺寸滑块。选择写进浏览器本地存储，",
        "与下面的 Expo 相册互不影响。",
        "", NOTICE, "",
    ]) + "\n")

    for slug, w, h, rgb, freq, title, desc, tags, date in BLOG:
        d = os.path.join(blog, slug)
        os.makedirs(d, exist_ok=True)
        n = write_png(os.path.join(d, "featured.png"), w, h, rgb, freq)
        write(os.path.join(d, "index.md"), fm({
            "title": title, "description": desc, "date": date,
            "tags": tags, "weight": len(tags),
        }) + "\n".join([
            "", "封面 `%s` %d×%d 像素（PNG %d 字节），由脚本生成。" % (slug, w, h, n),
            "",
            "## 这张图看什么",
            "",
            "条目页只放一张封面加一段说明，用来验证 gallery 索引点开后的落地形态：",
            "标题、日期、标签、正文与上一篇/下一页导航都在。",
            "",
            "## 元数据",
            "",
            "| 字段 | 值 |",
            "|------|----|",
            "| 封面尺寸 | %d × %d |" % (w, h),
            "| 标签 | %s |" % "、".join(tags),
            "| 日期 | %s |" % date,
            "", NOTICE, "",
        ]) + "\n")
        made.append(("blog/" + slug, w, h, n))

    albums = os.path.join(root, "content", "albums")
    os.makedirs(albums, exist_ok=True)
    write(os.path.join(albums, "_index.md"), fm({
        "title": "相册", "description": "按作业批次组织的 Expo 相册，图片走 bundle 内的 images/* 目录。",
        "type": "expo",
    }) + "\n".join(["", "这一节是 Expo 相册（主题的第五种阅读外壳），与上面的 gallery 索引是两套东西：",
                    "gallery 排的是「条目 + 封面」，Expo 排的是「一个相册里的多图」。", "", NOTICE, ""]) + "\n")

    for aslug, atitle, adesc, amode, asize, shots in ALBUMS:
        d = os.path.join(albums, aslug)
        idir = os.path.join(d, "images")
        os.makedirs(idir, exist_ok=True)
        for (sslug, w, h, rgb, cap) in shots:
            n = write_png(os.path.join(idir, sslug + ".png"), w, h, rgb, 6)
            made.append(("albums/%s/images/%s" % (aslug, sslug), w, h, n))
        write(os.path.join(d, "index.md"), fm({
            "title": atitle, "description": adesc, "date": "2026-10-20",
            # Hugo 的页面 .Type 默认取 section 名（这里是 albums），
            # 不显式写 type: expo 就走不到 layouts/expo/single.html，相册不出图。
            "type": "expo",
            "expo": {"images": "images/*", "mode": amode, "size": asize},
        }) + "\n".join([
            "", "相册内 %d 张图放在 bundle 的 `images/` 下，由 front matter 的 `expo.images` 选中；" % len(shots),
            "`expo.mode: %s`、`expo.size: %d` 覆盖站点默认。" % (amode, asize),
            "",
            "| 图 | 尺寸 | 说明 |",
            "|----|------|------|",
        ] + ["| %s | %d × %d | %s |" % (s[0], s[1], s[2], s[3]) for s in shots] + [
            "", NOTICE, "",
        ]) + "\n")
    return made


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    items = build(root)
    print("generated_files=%d png=%d" % (len(items) + 4, len(items)))
    big = [i for i in items if i[1] * i[2] >= 960 * 960 or max(i[1], i[2]) > 960]
    print("png_total_bytes=%d" % sum(i[3] for i in items))
