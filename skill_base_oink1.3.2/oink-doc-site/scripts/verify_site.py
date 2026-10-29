"""统一验收入口：一条命令跑完计划、脚手架、构建、审计、链接与预设判据。

用法：
  python verify_site.py --site <站点目录> --plan site.plan.json --mode full|skeleton
                        [--min-lines 260] [--hugo <hugo可执行文件>] [--go-bin <go的bin目录>]
                        [--skip-build] [--report out.md]
  python verify_site.py --selftest

退出码：0 = 全部自动/构建判据通过；1 = 有 FAIL；2 = 用法错。

判据分三类，汇总里分开写，别把 MANUAL 当 PASS：
  AUTO    计划、脚手架、结构审计、站内链接、案例包、交付文档
  BUILD   hugo build、产物里的 data-td-preset 与顶栏 docs 入口（给了 --hugo 才跑）
  MANUAL  Mermaid 真解析（只生成解析台）、内容来源清单

判据先要能红：`--selftest` 会跑六个子脚本的自证，并在假站点上注入
「占位符 / 缺 data-td-preset / 缺顶栏入口 / 缺 T0 文档 / 坏计划 / 案例包 static 副本缺失 /
缺 run.cmd / run.cmd 缺标记」八类缺陷，逐条确认会报 FAIL。
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import audit_content  # noqa: E402
import check_cases  # noqa: E402
import check_links  # noqa: E402
import package_case  # noqa: E402
import plan_site  # noqa: E402

HUGO_ENV = {"GOTOOLCHAIN": "local", "GOPROXY": "off"}
MANUAL_STATUS = ("MANUAL", "GENERATED", "PRESENT")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run_cmd(cmd, cwd=None, env=None, timeout=300):
    e = dict(os.environ, PYTHONIOENCODING="utf-8")
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, str(exc)


def count_files(root):
    return sum(len(fs) for _, _, fs in os.walk(root))


def active_value(text, key):
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*" + re.escape(key) + r":\s*(.+?)\s*$", line)
        if m:
            return m.group(1)
    return None


def scan_placeholders(site):
    hits = {}
    roots = [os.path.join(site, "content"), os.path.join(site, "data")]
    targets = [os.path.join(site, "hugo.yaml"), os.path.join(site, "README.md")]
    for dp, dns, fns in os.walk(site):
        dns[:] = [d for d in dns if d not in ("oink-main", "public", "resources", ".git", ".tmp", "doc")]
        for f in fns:
            if f.endswith((".md", ".yaml", ".yml", ".html")):
                targets.append(os.path.join(dp, f))
    seen = set()
    for p in targets:
        if not os.path.isfile(p) or p in seen:
            continue
        seen.add(p)
        try:
            text = read(p)
        except (OSError, UnicodeDecodeError):
            continue
        n = text.count("【")
        if n:
            hits[os.path.relpath(p, site).replace(os.sep, "/")] = n
    return hits


def theme_info(site):
    theme = os.path.join(site, "oink-main", "oink-main")
    required = ("theme.toml", "hugo.yaml", "assets/scss/td/_presets.scss",
                "layouts/_partials/preset-config.html",
                "assets/third_party/mermaid/mermaid.min.js")
    missing = [p for p in required if not os.path.isfile(os.path.join(theme, p))]
    if missing:
        return None, missing, 0
    return theme, [], count_files(theme)


def gate_plan(plan_path):
    try:
        data = json.load(io.open(plan_path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return "FAIL", "读计划失败：%s" % e
    problems, summary = plan_site.check_plan(data)
    detail = "categories=%d sections=%d articles=%d problems=%d" % (
        summary.get("categories", 0), summary.get("sections", 0),
        summary.get("articles", 0), len(problems))
    return ("PASS" if not problems else "FAIL"), detail


RUN_CMD_MARKERS = (
    'set "GOTOOLCHAIN=local"',
    'set "GOPROXY=off"',
    "HUGO_EXE",
    "NO_OPEN",
    "NO_PAUSE",
    "--openBrowser",
    'set "SITE_TITLE=',
)


def check_run_cmd(site):
    """run.cmd 是交付物：存在、ASCII、CRLF、带离线与启动契约标记。"""
    path = os.path.join(site, "run.cmd")
    if not os.path.isfile(path):
        return "缺 run.cmd（拷 assets/scaffold/run.cmd 并只改 PROJECT CONFIG 块）"
    with open(path, "rb") as f:
        raw = f.read()
    if b"\r\n" not in raw:
        return "run.cmd 不是 CRLF 行尾"
    if any(b > 127 for b in raw):
        if b"chcp 65001" not in raw:
            return "run.cmd 含非 ASCII 但缺 chcp 65001（中文显示会丢字节）"
        if raw.startswith(b"\xef\xbb\xbf"):
            return "run.cmd 带 UTF-8 BOM（cmd 解析会出错）"
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return "run.cmd 非 ASCII 且不是合法 UTF-8"
    else:
        text = raw.decode("ascii")
    missing = [m for m in RUN_CMD_MARKERS if m not in text]
    if missing:
        return "run.cmd 缺契约标记：%s（旧模板请整体换成 assets/scaffold/run.cmd）" % "、".join(missing)
    return None


def gate_scaffold(site, plan_data):
    theme, missing, n_theme = theme_info(site)
    if missing:
        return "FAIL", "主题副本不完整，缺：%s" % "、".join(missing)
    minv = re.search(r'min_version\s*=\s*"([^"]+)"', read(os.path.join(theme, "theme.toml")))
    if not minv or tuple(int(x) for x in minv.group(1).split(".")[:3]) < (0, 166, 0):
        return "FAIL", "主题 min_version 不是 0.166.0：%s" % (minv.group(1) if minv else "缺失")
    hugo = os.path.join(site, "hugo.yaml")
    if not os.path.isfile(hugo):
        return "FAIL", "缺 hugo.yaml"
    text = read(hugo)
    needed = {
        "relativeURLs: true": "relativeURLs: true",
        "unsafe: true": "renderer:\n      unsafe: true",
        "block: true": "attribute:\n        block: true",
        "wrapStandAloneImageWithinParagraph: false": "wrapStandAloneImageWithinParagraph: false",
        "noClasses: false": "noClasses: false",
        "offline_search: true": "offline_search: true",
        "replace 本地主题": "replacement: ./oink-main/oink-main",
    }
    for label, needle in needed.items():
        if needle not in text:
            return "FAIL", "hugo.yaml 缺主题契约项：%s" % label
    site_cfg = plan_data.get("site", {})
    preset = site_cfg.get("preset", "paper")
    menu = site_cfg.get("presetMenu", list(plan_site.PRESETS))
    got_preset = active_value(text, "preset")
    got_menu = active_value(text, "preset_menu")
    if got_preset is None:
        return "FAIL", "hugo.yaml 的 preset 缺失或被注释"
    if got_preset.strip("\"'") != preset:
        return "FAIL", "hugo.yaml 的 preset=%s 与计划 %s 不一致" % (got_preset, preset)
    if got_menu is None:
        return "FAIL", "hugo.yaml 的 preset_menu 缺失或被注释"
    if menu is False:
        if got_menu != "false":
            return "FAIL", "plan 要求单预设，但 preset_menu=%s" % got_menu
    elif menu is True:
        if got_menu != "true":
            return "FAIL", "plan 要求 preset_menu=true，但实际 %s" % got_menu
    else:
        parsed = [x.strip() for x in got_menu.strip("[]").split(",") if x.strip()]
        if parsed != menu:
            return "FAIL", "preset_menu=%s 与计划 %s 不一致" % (parsed, menu)
        if preset not in parsed:
            return "FAIL", "preset_menu 不含默认 preset=%s" % preset
    for rel in ("content/_index.md", "content/docs/_index.md", "data/home/zh.yaml", "README.md"):
        if not os.path.isfile(os.path.join(site, rel)):
            return "FAIL", "缺生成文件 %s" % rel
    hits = scan_placeholders(site)
    if hits:
        return "FAIL", "仍有【】占位：%s" % "、".join("%s(%d)" % (k, v) for k, v in sorted(hits.items())[:6])
    err = check_run_cmd(site)
    if err:
        return "FAIL", err
    return "PASS", "theme_files=%d placeholders=0 preset=%s run_cmd=ok" % (n_theme, preset)


def parse_hugo_output(out):
    pages = re.search(r"^\s*Pages\s*[│|]\s*(\d+)", out, re.M)
    static = re.search(r"^\s*Static files\s*[│|]\s*(\d+)", out, re.M)
    parts = []
    if pages:
        parts.append("Pages=%s" % pages.group(1))
    if static:
        parts.append("Static files=%s" % static.group(1))
    return " ".join(parts)


def gate_build(site, hugo, go_bin, skip_build):
    if not hugo or skip_build:
        return "SKIP", "未给 --hugo 或 --skip-build"
    env = dict(HUGO_ENV)
    if go_bin:
        env["PATH"] = os.path.abspath(go_bin) + os.pathsep + os.environ.get("PATH", "")
    rc, out = run_cmd([hugo, "--cleanDestinationDir"], cwd=site, env=env, timeout=300)
    err = len(re.findall(r"ERROR", out))
    detail = "%s ERROR=%d rc=%d" % (parse_hugo_output(out) or "no-pages-line", err, rc)
    if 'binary with name "go" not found' in out or "failed to load modules" in out:
        detail += "；缺 go 或模块解析失败：用 --go-bin <go的bin目录>"
    if "extended" in out.lower() and rc != 0:
        detail += "；疑似非 Extended Hugo（主题要 SCSS 编译）"
    status = "PASS" if rc == 0 and err == 0 and os.path.isfile(os.path.join(site, "public", "index.html")) else "FAIL"
    return status, detail


def gate_preset(site, plan_data):
    index = os.path.join(site, "public", "index.html")
    if not os.path.isfile(index):
        return "SKIP", "无 public/index.html（构建没跑）"
    html = read(index)
    preset = plan_data.get("site", {}).get("preset", "paper")
    html_tag = re.search(r"<html\b[^>]*>", html, re.S)
    if not html_tag or not re.search(
            r'data-td-preset\s*=\s*["\']?%s["\']?' % re.escape(preset), html_tag.group(0)):
        return "FAIL", ("public/index.html 的 <html> 上没有 data-td-preset=\"%s\"；"
                        "主题副本可能是 1.0/1.1，或 preset 配置被注释" % preset)
    menu = plan_data.get("site", {}).get("presetMenu", list(plan_site.PRESETS))
    if isinstance(menu, list) and len(menu) > 1:
        missing = [x for x in menu if x not in html]
        if missing:
            return "FAIL", "产物里找不到预设名：%s（Appearance 菜单可能没开）" % "、".join(missing)
    return "PASS", "data-td-preset=%s menu=%s" % (
        preset, "list:%d" % len(menu) if isinstance(menu, list) else menu)


def gate_nav(site):
    """顶栏 docs 入口：OINK 只渲染 menus.main，主题不会自动挂 docs。"""
    index = os.path.join(site, "public", "index.html")
    if not os.path.isfile(index):
        return "SKIP", "无 public/index.html（构建没跑）"
    html = read(index)
    zone = re.search(r'<div[^>]*td-nav-menu-zone[^>]*>(.*?)</div>', html, re.S)
    if not zone:
        return "FAIL", "public/index.html 没有顶栏菜单容器 .td-nav-menu-zone"
    chunk = zone.group(1)
    for tag in re.findall(r"<a\b[^>]*>", chunk, re.S):
        m = re.search(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", tag)
        if not m:
            continue
        href = next(g for g in m.groups() if g is not None)
        if re.search(r"(^|/)docs/?($|[?#])", href):
            return "PASS", "顶栏「文档」入口存在"
    return "FAIL", "顶栏菜单没有指向 docs 的入口；检查 hugo.yaml 的 menus.main"


def gate_audit(site, plan_path, mode, min_lines, report):
    try:
        problems, rows, stats = audit_content.audit(site, plan_path, mode, min_lines)
    except (OSError, ValueError) as e:
        return "FAIL", str(e)
    if report:
        audit_content.write_report(report + ".audit.md", rows, problems, stats)
    detail = "articles=%d expected=%d problems=%d mode=%s genre_checks=%d" % (
        stats["articles"], stats["expected"], stats["problems"], stats["mode"], stats["genre_checks"])
    return ("PASS" if not problems else "FAIL"), detail


def gate_links(site):
    if not os.path.isdir(os.path.join(site, "public")):
        return "SKIP", "无 public/（构建没跑）"
    try:
        broken, unmapped, stats = check_links.check(site)
    except OSError as e:
        return "SKIP", str(e)
    detail = "links_checked=%d broken=%d unmapped=%d home_urls=%d" % (
        stats["checked"], len(broken), len(unmapped), stats["home_urls"])
    return ("PASS" if not (broken or unmapped) else "FAIL"), detail


def gate_cases(site):
    """实验验证案例包：源目录、zip、static 副本、文档引用四方一致。"""
    if not os.path.isdir(os.path.join(site, "cases")):
        return "SKIP", "无 cases/，本轮没有实验验证案例"
    try:
        problems, stats = check_cases.check(site)
    except OSError as e:
        return "FAIL", str(e)
    detail = "cases=%d doc_links=%d public=%s problems=%d" % (
        stats["cases"], stats["doc_links"], stats["public"], len(problems))
    if problems:
        detail += "；首条：" + "%s %s" % (problems[0][0], problems[0][1])
    return ("PASS" if not problems else "FAIL"), detail


def gate_mermaid(site):
    theme, missing, _ = theme_info(site)
    if missing:
        return "FAIL", "主题不完整，无法生成解析台"
    out_dir = os.path.join(site, "_mermaid-harness")
    cmd = [sys.executable, os.path.join(HERE, "validate_mermaid.py"), "--site", site,
           "--selftest", "--out", out_dir,
           "--mermaid-js", os.path.join(theme, "assets", "third_party", "mermaid", "mermaid.min.js")]
    rc, out = run_cmd(cmd, timeout=120)
    m = re.search(r"blocks=(\d+)", out)
    blocks = m.group(1) if m else "?"
    detail = "blocks=%s out=%s；需按脚本三步在浏览器读回 REAL_FAIL=0" % (blocks, out_dir)
    return ("GENERATED" if rc == 0 else "FAIL"), detail


def gate_delivery(site, mode):
    if mode != "full":
        return "SKIP", "skeleton 模式不要求交付文档（交付前切 --mode full）"
    path = os.path.join(site, "doc", "运行与构建（T0Level）.md")
    if not os.path.isfile(path):
        return "FAIL", "缺 doc/运行与构建（T0Level）.md"
    text = read(path)
    if "【" in text:
        return "FAIL", "T0Level 文档仍有【】占位"
    if "hugo" not in text or "verify_site.py" not in text:
        return "FAIL", "T0Level 文档未写入 hugo 与 verify_site.py 的真实命令"
    if len(re.findall(r"^##\s+", text, re.M)) < 6:
        return "FAIL", "T0Level 文档少于 6 个 H2 小节"
    return "PASS", "doc/运行与构建（T0Level）.md 已落地"


def gate_ledger(site):
    path = os.path.join(site, "doc", "内容来源.md")
    if os.path.isfile(path):
        return "PRESENT", "doc/内容来源.md 已存在，需人工核对来源是否覆盖全部事实"
    return "MANUAL", "未生成 doc/内容来源.md；写具体事实时必须登记来源"


def gates(args):
    site = os.path.abspath(args.site)
    plan_path = os.path.abspath(args.plan)
    try:
        plan_data = json.load(io.open(plan_path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [("plan", "AUTO", "FAIL", "读计划失败：%s" % e)]
    rows = [
        ("plan", "AUTO") + gate_plan(plan_path),
        ("scaffold", "AUTO") + gate_scaffold(site, plan_data),
        ("build", "BUILD") + gate_build(site, args.hugo, args.go_bin, args.skip_build),
        ("preset", "BUILD") + gate_preset(site, plan_data),
        ("nav", "BUILD") + gate_nav(site),
        ("audit", "AUTO") + gate_audit(site, plan_path, args.mode, args.min_lines, args.report),
        ("links", "AUTO") + gate_links(site),
        ("cases", "AUTO") + gate_cases(site),
        ("mermaid", "MANUAL") + gate_mermaid(site),
        ("delivery_doc", "AUTO") + gate_delivery(site, args.mode),
        ("source_ledger", "MANUAL") + gate_ledger(site),
    ]
    return rows


def print_rows(rows, report=None):
    width = max(len(r[0]) for r in rows)
    print("%-*s  %-6s  %-9s  %s" % (width, "判据", "类别", "状态", "摘要"))
    for name, kind, status, detail in rows:
        print("%-*s  %-6s  %-9s  %s" % (width, name, kind, status, detail))
    fails = [r for r in rows if r[2] == "FAIL"]
    manuals = [r for r in rows if r[2] in MANUAL_STATUS]
    print("FAIL=%d MANUAL=%d PASS=%d SKIP=%d" % (
        len(fails), len(manuals), sum(1 for r in rows if r[2] == "PASS"),
        sum(1 for r in rows if r[2] == "SKIP")))
    if manuals:
        print("提醒：MANUAL 项没有结论，别把它当通过——Mermaid 要在浏览器读回 REAL_FAIL=0，来源清单要人工核对。")
    if report:
        write(report, "# 验收汇总\n\n| 判据 | 类别 | 状态 | 摘要 |\n|---|---|---|---|\n"
              + "".join("| `%s` | %s | %s | %s |\n" % (n, k, s, d.replace("|", "/"))
                        for n, k, s, d in rows))
    return 1 if fails else 0


def fake_site(root, with_plan_doc=True):
    site = os.path.join(root, "site")
    theme = os.path.join(site, "oink-main", "oink-main")
    os.makedirs(os.path.join(theme, "assets", "scss", "td"), exist_ok=True)
    os.makedirs(os.path.join(theme, "layouts", "_partials"), exist_ok=True)
    os.makedirs(os.path.join(theme, "assets", "third_party", "mermaid"), exist_ok=True)
    write(os.path.join(theme, "theme.toml"), 'name = "OINK"\nmin_version = "0.166.0"\n')
    write(os.path.join(theme, "hugo.yaml"), "params: {}\n")
    write(os.path.join(theme, "assets", "scss", "td", "_presets.scss"), "/* preset */\n")
    write(os.path.join(theme, "layouts", "_partials", "preset-config.html"), "<!-- preset -->\n")
    write(os.path.join(theme, "assets", "third_party", "mermaid", "mermaid.min.js"), "/* mermaid */\n")
    write(os.path.join(site, "content", "_index.md"), "---\ntitle: \"示例\"\ndescription: \"示例\"\n---\n")
    write(os.path.join(site, "content", "docs", "_index.md"), "---\ntitle: \"文档\"\ndescription: \"文档\"\n---\n")
    write(os.path.join(site, "data", "home", "zh.yaml"), "sections: [hero]\n")
    write(os.path.join(site, "README.md"), "# 示例\n")
    shutil.copyfile(os.path.join(SKILL, "assets", "scaffold", "run.cmd"),
                    os.path.join(site, "run.cmd"))
    hugo = read(os.path.join(SKILL, "assets", "templates", "hugo.yaml"))
    repl = {
        "【站点标题】": "示例文档", "【BASE_URL】": "https://example.org/",
        "【站点摘要】": "示例文档摘要", "【版权主体】": "示例",
        "【起始年】": "2026", "【页脚说明】": "示例", "【PRESET】": "paper",
        "【PRESET_MENU】": "[paper, slate, ink, terminal]",
    }
    for k, v in repl.items():
        hugo = hugo.replace(k, v)
    write(os.path.join(site, "hugo.yaml"), hugo)
    if with_plan_doc:
        write(os.path.join(site, "doc", "运行与构建（T0Level）.md"),
              "# T0\n\n## 一\n\n## 二\n\n## 三\n\n## 四\n\n## 五\n\n## 六\n\n"
              "hugo --cleanDestinationDir\npython verify_site.py\n")
    plan = {
        "site": {"title": "示例文档", "description": "示例文档摘要",
                 "baseURL": "https://example.org/", "preset": "paper",
                 "presetMenu": ["paper", "slate", "ink", "terminal"]},
        "categories": [{"dir": "01-cat", "title": "分类", "weight": 1, "desc": "分类描述",
                        "sections": [{"dir": "sec", "title": "板块", "weight": 1,
                                      "desc": "板块描述", "articles": [
                                          {"file": "good.md", "title": "合规样本", "weight": 1,
                                           "desc": "这是一篇用于验证审计绿灯的合规样本，描述超过二十个字。"}]}]}],
    }
    plan_path = os.path.join(root, "plan.json")
    write(plan_path, json.dumps(plan, ensure_ascii=False, indent=1))
    return site, plan_path, plan


def add_case_fixture(site, theme, case):
    """在假站点里造一个四方齐全的最小完整案例：.gitignore + 手册 + 脚本，交给 package_case 打包。"""
    cdir = os.path.join(site, "cases", theme, case)
    write(os.path.join(cdir, ".gitignore"), check_cases.BASELINE_IGNORE)
    write(os.path.join(cdir, "README.md"), check_cases.GOOD_MANUAL)
    write(os.path.join(cdir, "probe.cmd"), "netstat -ano\n")
    zp = package_case.pack(site, theme, case)[0]
    # 构建后 static 副本会落进 public/；假站点已经有 public/，这里同步一份免得误报 NOT_IN_PUBLIC
    os.makedirs(os.path.join(site, "public", "cases", theme), exist_ok=True)
    shutil.copyfile(zp, os.path.join(site, "public", "cases", theme, case + ".zip"))
    write(os.path.join(site, "content", "case-ref.md"),
          "[%s.zip](/cases/%s/%s.zip)\n" % (case, theme, case))
    return zp


def selftest():
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-verify-", dir=os.path.abspath(root))
    ok = True
    try:
        sub = [
            ("plan_site", [sys.executable, os.path.join(HERE, "plan_site.py"), "--selftest"]),
            ("audit_content", [sys.executable, os.path.join(HERE, "audit_content.py"), "--selftest"]),
            ("check_links", [sys.executable, os.path.join(HERE, "check_links.py"), "--selftest"]),
            ("check_cases", [sys.executable, os.path.join(HERE, "check_cases.py"), "--selftest"]),
            ("package_case", [sys.executable, os.path.join(HERE, "package_case.py"), "--selftest"]),
        ]
        for name, cmd in sub:
            rc, out = run_cmd(cmd, timeout=180)
            good = rc == 0 and "SELFTEST_PASS" in out
            print("%s --selftest: rc=%d %s" % (name, rc, "PASS" if good else "FAIL"))
            if not good:
                ok = False
                print(out[-800:])

        fixtures = os.path.join(SKILL, "assets", "fixtures")
        theme_mermaid = os.path.join(SKILL, "assets", "theme", "oink-main", "oink-main",
                                     "assets", "third_party", "mermaid", "mermaid.min.js")
        rc, out = run_cmd([sys.executable, os.path.join(HERE, "validate_mermaid.py"),
                           "--site", os.path.join(fixtures, "site"), "--selftest",
                           "--mermaid-js", theme_mermaid,
                           "--out", os.path.join(tmp, "harness")], timeout=120)
        good = rc == 0 and "SELFTEST_PASS" in out
        print("validate_mermaid --selftest: rc=%d %s" % (rc, "PASS" if good else "FAIL"))
        if not good:
            ok = False
            print(out[-800:])

        site, plan_path, _ = fake_site(tmp)
        st, detail = gate_scaffold(site, json.load(io.open(plan_path, encoding="utf-8")))
        print("scaffold green: %s %s" % (st, detail))
        if st != "PASS":
            ok = False
        # 注入占位符：必须红
        hugo_path = os.path.join(site, "hugo.yaml")
        saved = read(hugo_path)
        write(hugo_path, saved + "\n# 【INJECTED】\n")
        st_bad, _ = gate_scaffold(site, json.load(io.open(plan_path, encoding="utf-8")))
        print("scaffold placeholder injected: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        write(hugo_path, saved)
        # run.cmd：缺文件 / 缺契约标记 必须红
        run_path = os.path.join(site, "run.cmd")
        with open(run_path, "rb") as f:
            saved_run = f.read()
        plan_data = json.load(io.open(plan_path, encoding="utf-8"))
        os.remove(run_path)
        st_bad, _ = gate_scaffold(site, plan_data)
        print("run.cmd missing injected: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        with open(run_path, "wb") as f:
            f.write(saved_run.replace(b'set "GOPROXY=off"\r\n', b""))
        st_bad, _ = gate_scaffold(site, plan_data)
        print("run.cmd marker injected: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        with open(run_path, "wb") as f:
            f.write(saved_run)
        st_good, _ = gate_scaffold(site, plan_data)
        print("run.cmd restored: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # 注入缺 data-td-preset / 缺顶栏入口：必须红
        write(os.path.join(site, "public", "index.html"), "<!doctype html><html><body></body></html>\n")
        plan_data = json.load(io.open(plan_path, encoding="utf-8"))
        st_bad, _ = gate_preset(site, plan_data)
        print("preset missing injected: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        st_bad, _ = gate_nav(site)
        print("nav missing injected: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        good_html = ('<!doctype html><html data-td-preset="paper"><body>paper slate ink terminal'
                     '<div class="td-nav-links td-nav-menu-zone">'
                     '<a class="nav-link" href="./docs/" data-td-navbar-label="文档">文档</a>'
                     '</div></body></html>\n')
        write(os.path.join(site, "public", "index.html"), good_html)
        st_good, _ = gate_preset(site, plan_data)
        print("preset restored: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        st_good, _ = gate_nav(site)
        print("nav restored: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # Hugo --minify 会把简单属性值去掉引号，判据必须同样接受
        min_html = ('<!doctype html><html data-td-preset=paper><body>paper slate ink terminal'
                    '<div class="td-nav-links td-nav-menu-zone">'
                    '<a class=nav-link href=./docs/>文档</a></div></body></html>\n')
        write(os.path.join(site, "public", "index.html"), min_html)
        st_good, _ = gate_preset(site, plan_data)
        print("preset minified: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        st_good, _ = gate_nav(site)
        print("nav minified: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # 交付文档：缺文件 / 有占位 / 完整
        doc = os.path.join(site, "doc", "运行与构建（T0Level）.md")
        os.remove(doc)
        st_bad, _ = gate_delivery(site, "full")
        print("delivery missing: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        write(doc, "# T0\n\n## 一\n\n【待填】\n")
        st_bad, _ = gate_delivery(site, "full")
        print("delivery placeholder: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        write(doc, "# T0\n\n## 一\n\n## 二\n\n## 三\n\n## 四\n\n## 五\n\n## 六\n\n"
                  "hugo --cleanDestinationDir\npython verify_site.py\n")
        st_good, _ = gate_delivery(site, "full")
        print("delivery restored: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # 计划：坏计划必须红，好计划必须绿
        st_bad, _ = gate_plan(os.path.join(fixtures, "plan.json"))
        print("plan fixture: %s（期望 FAIL）" % st_bad)
        if st_bad != "FAIL":
            ok = False
        st_good, _ = gate_plan(plan_path)
        print("plan good: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # 审计：把合规样本放进假站点，必须绿
        docs = os.path.join(site, "content", "docs", "01-cat", "sec")
        os.makedirs(docs, exist_ok=True)
        write(os.path.join(site, "content", "docs", "01-cat", "_index.md"),
              "---\ntitle: \"分类\"\ndescription: \"分类描述\"\nweight: 1\n---\n")
        write(os.path.join(docs, "_index.md"),
              "---\ntitle: \"板块\"\ndescription: \"板块描述\"\nweight: 1\n---\n")
        good = read(os.path.join(fixtures, "site", "content", "docs", "01-分类", "合规板块", "good-1.md"))
        write(os.path.join(docs, "good.md"), good)
        st_good, detail = gate_audit(site, plan_path, "full", 20, None)
        print("audit green: %s %s" % (st_good, detail))
        if st_good != "PASS":
            ok = False
        st_bad, detail = gate_audit(os.path.join(fixtures, "site"),
                                    os.path.join(fixtures, "plan.json"), "full", 20, None)
        print("audit fixture: %s（期望 FAIL）%s" % (st_bad, detail))
        if st_bad != "FAIL":
            ok = False
        # 案例包：无 cases/ 必须 SKIP，四方齐全必须 PASS，缺 static 副本必须 FAIL
        st_skip, detail = gate_cases(site)
        print("cases absent: %s（期望 SKIP）%s" % (st_skip, detail))
        if st_skip != "SKIP":
            ok = False
        zp = add_case_fixture(site, "09-ops", "demo")
        st_good, detail = gate_cases(site)
        print("cases green: %s %s" % (st_good, detail))
        if st_good != "PASS":
            ok = False
        os.remove(os.path.join(site, "static", "cases", "09-ops", "demo.zip"))
        st_bad, detail = gate_cases(site)
        print("cases static deleted: %s（期望 FAIL）%s" % (st_bad, detail))
        if st_bad != "FAIL":
            ok = False
        shutil.copyfile(zp, os.path.join(site, "static", "cases", "09-ops", "demo.zip"))
        st_good, _ = gate_cases(site)
        print("cases restored: %s（期望 PASS）" % st_good)
        if st_good != "PASS":
            ok = False
        # Hugo 输出解析器：ERROR 必须被看见
        sample_ok = " Pages │ 15\n Static files │ 34\n Total in 1231 ms\n"
        sample_bad = " Pages │ 15\nERROR failed to build\n"
        parse_ok = parse_hugo_output(sample_ok) == "Pages=15 Static files=34"
        err_seen = len(re.findall(r"ERROR", sample_bad)) == 1
        print("hugo_output_parser: parse_ok=%s error_seen=%s" % (parse_ok, err_seen))
        if not (parse_ok and err_seen):
            ok = False
        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--plan")
    ap.add_argument("--mode", choices=("full", "skeleton"), default="full")
    ap.add_argument("--min-lines", type=int, default=260)
    ap.add_argument("--hugo")
    ap.add_argument("--go-bin")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.site or not a.plan:
        print("FAIL 需要 --site 与 --plan（或 --selftest）")
        sys.exit(2)
    rows = gates(a)
    sys.exit(print_rows(rows, a.report))


if __name__ == "__main__":
    main()
