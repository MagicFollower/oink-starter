# 实验验证案例包：口径、手册与判据

供 `SKILL.md` Step 5 使用。两条口径：**该不该有包**——正文里有一条结论是靠真实命令输出撑起来的
（性能数字、复现步骤、故障对照、协议实测），就要落成可复现案例包，纯概念与纯配置说明不需要；
**包对不对**——包必须「最小完整」，读者只看包内就能复现，依赖与产物一律不许混进去。

## 四方一致

一个案例同时存在四份东西，少任何一份 `check_cases.py` 直接红：

| 角色 | 路径 | 由谁产生 |
|------|------|----------|
| 排除清单 + 案例源目录 | `cases/<主题>/<案例>/`（`.gitignore`、`README.md`、脚本、必要数据） | 作者（`--init` 给基线） |
| 打包产物 | `cases/<主题>/<案例>.zip`，条目一律 `<案例>/` 前缀 + 正斜杠 | `package_case.py` |
| 发布副本 | `static/cases/<主题>/<案例>.zip`，与源 zip 字节一致 | `package_case.py` |
| 文档引用 | 至少一篇 `content/**/*.md` 用 Markdown 链接指向 `/cases/<主题>/<案例>.zip` | 作者 |

构建后 `static/cases/` 会进 `public/cases/`，读者才下载得到；这就是 `NOT_IN_PUBLIC` 判据存在的原因。

`<主题>` 用带序号的短目录名（`04-ops`、`06-store`），`<案例>` 用 kebab-case ASCII：zip 条目名带中文时
Windows 11 能读，老 WinRAR/7-Zip 可能乱码（本技能未实测旧版本）。

## 最小完整：`.gitignore` 是唯一排除来源

`package_case.py --init` 会在案例目录写一份 `.gitignore`，git 与打包共用它。基线排除这些依赖与产物：
`node_modules/`、`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`.pytest_cache/`、`.mypy_cache/`、
`.ruff_cache/`、`.pnpm-store/`、`dist/`、`build/`、`out/`、`target/`、`coverage/`、`.idea/`、
`.vscode/`、`.tmp/`、`.DS_Store`、`Thumbs.db`、`desktop.ini`。

- 匹配语义是子集：只支持 `dir/`、`*.ext`、`path/` 三种形态，`!` 反向规则被忽略。
- 这批目录与后缀还有一份硬排除兜底：即使 `.gitignore` 被删空，`node_modules`、`__pycache__`、
  `.venv`、`dist`、`build`、`*.pyc` 进了包也判 `DEP_IN_ZIP`。宁可报红，也不静默剔除——
  静默会让作者以为包里全了。
- 密钥类直接拒绝打包：`.env`、`.netrc`、`credentials.json`、`secrets.json`、`id_rsa`、`*.pem`、
  `*.key`、`*.p12`、`*.pfx`、`*.jks`。要留样本就写成 `.env.example` 之类的脱敏文件。
- 单文件超过 `--max-file-kb`（默认 10240 = 10 MiB，按未压缩大小判定）拒绝打包；检查侧对应
  `OVERSIZE_FILE`。这类产物写「再生成命令」，不入库。
- 判据也要求包完整：`<案例>/README.md` 必须在 zip 里，否则 `NO_MANUAL_IN_ZIP`——
  读者下载到一个没有手册的包等于没交付。

实测口径：案例目录里放 `node_modules/dep/i.js`、`__pycache__/a.pyc`、`result.log` 后打包，
得到 `entries=4 excluded=2`，包内是 `.gitignore`、`README.md`、`result.log`、`run.cmd`——
依赖没进来，作为证据的日志留着。

## 手册（介绍与使用手册）

`cases/<主题>/<案例>/README.md` 必需 8 个 H2 小节，且每节都要有正文：缺小节报 `MANUAL_SECTION`，
只有标题没内容报 `MANUAL_THIN`，残留全角中括号占位报 `MANUAL_PLACEHOLDER`。模板在
`assets/templates/case-README.md`，`package_case.py --init` 会拷它。

```text
## 案例简介        验证文档里的哪一条结论；为什么必须真跑
## 适用文档        引用本包的文章 URL 与章节，至少一条
## 前置条件        系统/工具链/被测版本/数据准备/权限，数值写来源
## 运行步骤        工作目录 + 完整命令 + 预期耗时
## 预期结果与判据   可机器检：命令、期望输出、失败时长什么样，含一条「判据先证明会红」
## 包内容清单      解压后的文件树与每个文件的作用
## 复现记录        最近一次真实复现的日期、机器、真实数字；没跑的写「未验证」+ 原因
## 清理与回滚      删哪些产物、还原哪些配置、要不要重启
```

手册随 zip 分发，读者不看站点也能复现；站点正文只负责「为什么做这个实验」和「结论」，不复制手册全文。

## 命令

```bash
# 1) 建骨架：写 .gitignore + 手册模板（占位保留）
python <技能目录>/scripts/package_case.py --site <站点目录> --theme <主题> --case <案例> --init
# 2) 填手册、放脚本与必要数据
# 3) 打包（手册不合格 / 有密钥 / 超限文件 → 拒绝并退出 1）
python <技能目录>/scripts/package_case.py --site <站点目录> --theme <主题> --case <案例> [--max-file-kb 10240]
# 4) 在用到它的文章里加下载链接，然后 hugo --cleanDestinationDir 重构建
# 5) 判据
python <技能目录>/scripts/check_cases.py --site <站点目录> [--max-file-kb 10240]
```

第 3 步成功后会顺带打印 `check_cases ... problems=N`；`N>0` 时退出码 1，别忽略——刚建完包时
`UNREFERENCED` 与 `NOT_IN_PUBLIC` 两条红是预期的，加完链接并重构建后必须归零。

`verify_site.py` 汇总表里的 `cases` 行：无 `cases/` 时 `SKIP`，有案例时按 `check_cases` 结论给
`PASS`/`FAIL`。

## 文档里的引用写法

在用到该案例的文章末尾加一节，链接必须是真实 Markdown 链接（写进行内代码或注释里不算引用）：

```markdown
## 实验案例包

本节的判据来自可复现案例包：[kv-tuning.zip](/cases/06-store/kv-tuning.zip)。
解压后先读包内 `README.md`（介绍与使用手册），按其中的「运行步骤」与「预期结果与判据」复现。
```

## 错误码

| 码 | 含义 | 处理 |
|----|------|------|
| `NO_CASE_IGNORE` | 案例目录没有 `.gitignore` | 跑 `--init` 生成基线，再按需增删行 |
| `NO_MANUAL` | 案例目录里没有 `README.md` | 用 `--init` 建骨架后填写 |
| `MANUAL_SECTION` | 手册缺必需小节 | 按模板补齐 8 节 |
| `MANUAL_THIN` | 某小节只有标题没有正文 | 每节写实质内容，写不了就写「未验证」+ 原因 |
| `MANUAL_PLACEHOLDER` | 手册还有全角中括号占位没填 | 逐条填实 |
| `NO_ZIP` | `cases/<主题>/<案例>.zip` 不存在 | 跑 `package_case.py` |
| `EMPTY_ZIP` | zip 里没有文件 | 案例目录空，先放脚本/数据 |
| `BAD_ZIP_ENTRY` | 条目名带反斜杠、绝对路径或没以 `<案例>/` 开头 | 用 `package_case.py` 重打，别手搓 zip |
| `NO_MANUAL_IN_ZIP` | 包里没有手册 | 手册要在案例目录根；重打包 |
| `DEP_IN_ZIP` | 包里有 `node_modules`、`__pycache__`、`dist` 等依赖/产物 | 补 `.gitignore` 后重打包 |
| `SECRET_IN_ZIP` | 包里有 `.env`、`*.pem` 等疑似密钥 | 删除或脱敏；已发布的包要重打并撤旧包 |
| `OVERSIZE_FILE` | 单文件未压缩大小超 `--max-file-kb` | 改写「再生成命令」；确有必要再抬高上限 |
| `NO_STATIC_ZIP` | `static/cases/` 下没有发布副本 | 重跑 `package_case.py`（别只拷一次就删） |
| `ZIP_MISMATCH` | static 副本与 `cases/` 下的 zip 字节不同 | 改完源没重打包，重跑 |
| `UNREFERENCED` | 没有任何文档引用它 | 在对应文章加「实验案例包」小节 |
| `BROKEN_CASE_LINK` | 文档引用了不存在的案例包 | 改链接或补案例 |
| `NOT_IN_PUBLIC` | `public/cases/` 里没有该 zip | 重跑 `hugo --cleanDestinationDir`；仍缺就查部署有没有漏拷 |

## 坑

1. **只更新源、忘了重打包**：`ZIP_MISMATCH` 就是为这个准备的；改完案例必跑 `package_case.py`。
2. **把 zip 放进 `content/`**：Hugo 会把它当页面资源，URL 规则不可控。zip 只放 `cases/` 与 `static/cases/`。
3. **靠静默剔除保证干净**：`package_case.py` 会打印 `excluded=N` 与样例；别改成静默，也别绕过脚本手搓 zip。
4. **以为 `.gitignore` 支持全部 git 语法**：本技能只实现 `dir/`、`*.ext`、`path/` 三种形态，`!` 被忽略。
5. **把证据文件当依赖排除掉**：`*.log` 不在硬排除里，就是要留 `result.log` 这类复现证据；真要排除再往 `.gitignore` 加行。
6. **骨架阶段就引用案例**：`--mode skeleton` 不审正文，但 `cases` 判据照样咬四方一致；没有真实复现记录时先别建 `cases/`。
7. **案例与文档版本漂移**：被测版本变了要重跑，并在「复现记录」追加一行，不要只改正文数字。
8. **`public/` 被忽略是对的**：`public/cases/*.zip` 由构建产生，不入库；`cases/` 与 `static/cases/` 必须入库。
   站点根 `.gitignore` 基线已含 `cases/**/node_modules/`、`cases/**/*.env` 等条目。
