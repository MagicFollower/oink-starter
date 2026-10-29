# 站点计划（site.plan.json）

计划是**站点身份、首页、导航树与文章清单的唯一源数据**。`plan_site.py` 从它生成：

- `hugo.yaml`（标题、baseURL、语言、版权、视觉预设、顶栏 `menus.main` 的「文档」入口）
- `README.md`（项目结构、分类表、写作与构建口径）
- `content/_index.md`、`content/docs/_index.md`
- 每个分类/板块的 `_index.md`
- 每篇文章的 front matter 与文章桩
- `data/home/zh.yaml`（hero / cards / cta）

顶栏「文档」入口是模板级约定（OINK 只渲染 `.Site.Menus.main`，不会自动挂 docs），不在 `site.plan.json` 的 schema 内；`plan_site.py` 每次重写 `hugo.yaml` 时会保留它。

改导航先改计划再重跑；只手建目录会造成磁盘与计划漂移，`audit_content.py` 会报 `UNLISTED` / `NOT_WRITTEN`。

---

## 一、最小可用计划

```json
{
  "site": {
    "title": "产品文档",
    "description": "面向研发与运维的中文文档站，覆盖概念、上手与生产实践。",
    "baseURL": "https://docs.example.com/",
    "preset": "paper",
    "presetMenu": ["paper", "slate", "ink", "terminal"]
  },
  "categories": [
    {
      "dir": "01-overview",
      "title": "概览",
      "icon": "fa-solid fa-compass",
      "weight": 1,
      "desc": "先回答它是什么、为什么需要它、由哪些部分组成。",
      "sections": [
        {
          "dir": "认识系统",
          "title": "认识系统",
          "weight": 1,
          "desc": "从痛点与设计目标出发，建立整体心智模型。",
          "articles": [
            {
              "file": "what-is-it.md",
              "title": "它是什么，为什么需要它",
              "weight": 1,
              "desc": "从真实痛点出发，说明系统解决的问题、核心抽象与适用边界。",
              "sources": ["用户提供的项目简介"]
            }
          ]
        }
      ]
    }
  ]
}
```

完整三分类示例见 `assets/site.plan.example.json`，可直接复制成 `<站点>/site.plan.json` 后改。

## 二、字段约束

### site

| 字段 | 必填 | 约束 | 作用 |
|------|------|------|------|
| `title` | 是 | 非空 | 顶栏/标签页/页脚；首页标题的默认值 |
| `description` | 是 | 非空 | SEO、语言描述、首页导语默认值 |
| `baseURL` | 是 | `http://` 或 `https://` 开头 | canonical/RSS/llms.txt 的绝对链接；`relativeURLs: true` 下不影响本地打开 |
| `preset` | 否 | `paper`/`slate`/`ink`/`terminal`，默认 `paper` | 站点默认观感 |
| `presetMenu` | 否 | `true`/`false`/预设名数组，默认 4 套全开 | 读者可切换的外观列表；数组必须包含 `preset` |
| `lang` | 否 | 当前只支持 `zh` | 正文语言与审计口径 |
| `copyright.authors` | 否 | 字符串 | 页脚版权主体 |
| `copyright.fromYear` | 否 | 整数 | 页脚起始年 |
| `footer` | 否 | 字符串 | 页脚一行说明 |

### categories / sections / articles

| 层级 | 字段 | 约束 |
|------|------|------|
| 分类 | `dir` | 小写字母/数字/连字符，如 `01-overview`；会进 URL |
| 分类 | `title`/`desc` | 非空；`desc` 显示在侧边栏根卡片与首页卡片 |
| 分类 | `icon` | FontAwesome 类名，如 `fa-solid fa-compass`；缺省 `fa-solid fa-folder` |
| 分类 | `weight` | 1..N 连续不重复 |
| 板块 | `dir` | 中文或英文，不含空白/斜杠/`..`；会进 URL |
| 板块 | `title`/`desc` | 非空；`desc` 显示在板块卡片与侧边栏 |
| 板块 | `weight` | 同分类内 1..N 连续不重复 |
| 文章 | `file` | 普通 `.md`，不含空白/斜杠，不能是 `_index.md` |
| 文章 | `title`/`desc` | 非空；`desc` ≥ 20 字（会进卡片与 SEO） |
| 文章 | `weight` | 同板块内 1..N 连续不重复 |
| 文章 | `sources` | 可选字符串数组；写具体事实时登记来源，供 `doc/内容来源.md` 与人工复核使用 |

层级至少 1 个分类、每分类至少 1 个板块、每板块至少 1 篇文章。不要用空板块占位。

## 二之二、site.menu（docs 之外的顶栏入口）

规则：**`content/` 下每个一级 section 都要在顶栏有入口**。主题的阅读外壳有五种（`shell_types: [docs, book, blog, swagger, expo]`），所以文档、书籍、博客、接口文档、相册/图库都可能有独立页面，而 OINK 顶栏只渲染 `.Site.Menus.main`、生成器默认只写「文档」。`site.menu` 是可选数组，每条 `{name, url, weight}`：`name` 是顶栏显示名，`url` 必须是以 `/` 开头的站内路径（如 `/blog/`），`weight` 决定顺序（内置「文档」占 1）。生成器按 url 派生 `identifier` 并追加到 `menus.main`；`home.actions[].url` 与 `home.cta.url` 指向这些入口时校验放行。坏条目报 `BAD_MENU`（缺 name / url 非站内绝对路径 / 与 docs 撞车或彼此重复）。

为什么需要它：只建 docs 树时看不出问题，一旦站点有图库或博客，就会出现「页面都构建出来了、导航里没有任何入口」的静默缺口——构建零告警，只有去顶栏才看得出来。

这条由 `verify_site` 的 nav 判据兜住：它拿 `content/` 下的一级 section 逐个核对顶栏链接，缺就 FAIL 并点名。确实不挂顶栏的 section 写 `site.menuSkip: ["<目录名>"]`（例如只做重定向的过渡目录），判据放行并在摘要里标注。

## 三、URL 规则（最容易写错）

生成后的页面路径固定为：

```
/docs/<分类 dir>/<板块 dir>/<文章文件名去掉 .md>/
```

首页 `home.actions[].url`、`home.cta.url`、`home.cards[].url` 必须落在计划树内（或外链/锚点）。**文章页要写到板块层**：

```json
{ "url": "docs/01-overview/认识系统/what-is-it/" }
```

写成 `docs/01-overview/what-is-it/` 会通过计划 schema 但构建后断链；`plan_site.py` 现在用 `BAD_HOME_URL` 在写盘前拦住。`docs/` 与 `docs/<分类>/` 也可作为链接目标。

## 四、计划校验代码

`python scripts/plan_site.py --plan site.plan.json --check-only` 输出 `PLAN_OK` 或 `PLAN_INVALID`：

| 代码 | 含义 |
|------|------|
| `SCHEMA` | 字段缺失/类型不对/weight 非整数 |
| `NO_CATEGORIES` / `NO_ARTICLES` | 空分类或空板块 |
| `BAD_PATH` | 目录/文件名含空白、斜杠、`..`，或分类目录不是小写连字符 |
| `DUP_NAME` | 同级目录或文件重名 |
| `DUP_WEIGHT` / `WEIGHT_GAP` | 同级 weight 重复或不是 1..N |
| `THIN_DESC` | 文章 description 少于 20 字 |
| `BAD_PRESET` | 预设名非法，或 `presetMenu` 不含默认 `preset` |
| `BAD_BASE_URL` / `BAD_LANG` | baseURL 不是 http(s)，或语言不是 zh |
| `BAD_HOME` / `BAD_HOME_URL` | 首页字段类型不对，或 URL 不在计划树内 |

写盘后 `plan_site.py` 会再报 `articles_stubbed` / `articles_kept` / `placeholders_remaining`。`articles_kept` 是已存在且未被覆盖的文章；重跑计划不会冲掉正文，除非加 `--force`。

## 五、怎么设计导航

**按读者的任务组织，不按上游文件列表组织。**

- 一级分类 3–6 个，按认知顺序排：概览 → 快速开始 → 核心机制 → 操作/参考 → 运维排障。
- 每个分类 2–5 个板块；每个板块 2–6 篇文章。先保证每篇有明确读者问题，再谈数量。
- 一篇只归一个板块。跨板块关联用站内链接，不复制正文。
- 标题写具体任务（「第一次运行与结果验证」），不写宽泛名词（「使用」）。
- description 写「这篇解决什么问题」，不写「本文介绍……」。≥ 20 字，能直接进卡片。
- 计划里的 `sources` 是事实出处（用户材料、官方文档、真实命令输出）。没有来源的具体数值/默认值/异常语义不要写进正文。

## 六、生成与重跑

```bash
python scripts/scaffold.py --out <站点目录>
python scripts/plan_site.py --site <站点目录> --plan <站点目录>/site.plan.json --check-only
python scripts/plan_site.py --site <站点目录> --plan <站点目录>/site.plan.json
```

`plan_site.py` 总是重写：`hugo.yaml`、`README.md`、两个总览 `_index.md`、所有分类/板块 `_index.md`、`data/home/zh.yaml`。文章桩只在文件不存在时写；已写正文默认保留。要给文章换标题/描述/weight，直接改文章 front matter，或加 `--force` 重生成（会覆盖正文，慎用）。

## 七、范围限制

当前版本锁定**单语言中文站**。`lang` 非 `zh` 会被 `BAD_LANG` 拒绝；多语言站（`content/*.en.md`、`languages` 多分支）不在本技能内。要英文站，先复制本技能并改 `audit_content.py` 的 `NO_PAIN_OPEN` / `FEW_NEWBIE` / `ENGLISH_HEADING` 口径与写作规范，再放开 `lang`。
