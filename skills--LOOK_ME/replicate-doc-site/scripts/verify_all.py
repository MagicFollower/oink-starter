"""统一验收入口：一条命令跑完全部判据，并给出 PASS/FAIL/MANUAL 汇总。

用法：
  python verify_all.py --site <站点目录> --matrix matrix.json [--src <源根>] [--prefix tag=path]
                       [--skip-prefix tag] [--min-lines 260] [--mode rewrite|copy] [--scratch _work]
                       [--gate 0] [--hugo <hugo可执行文件>] [--go-bin <go的bin目录>]
                       [--skip-build] [--report out.md]
  python verify_all.py --selftest        # 用 assets/fixtures 证明每条判据都会红、合规样本都保持沉默

退出码：0 = 全部自动判据通过；1 = 有 FAIL；2 = 用法错。

判据分三类，汇总里分开写，别把 MANUAL 当 PASS：
  AUTO    本脚本直接跑完就有结论（结构审计、链接、矩阵、覆盖闸门）
  MANUAL  需要人/浏览器参与（mermaid 真解析：本脚本只生成解析台并核对注入样本）
  BUILD   需要 Hugo 与 Go 工具链（给了 --hugo 才跑）
"""

import argparse
import collections
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
FIXTURES = os.path.join(SKILL, "assets", "fixtures")


def run(cmd, cwd=None, extra_env=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if extra_env:
        env.update(extra_env)
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=cwd)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# 本地主题站必须离线构建：GOTOOLCHAIN=local 阻止 go 去下工具链，GOPROXY=off 阻止去拉模块。
# 少了这两个，Hugo 会卡在联网重试上，报出来的却是「failed to download modules」，看着像内容错。
HUGO_ENV = {"GOTOOLCHAIN": "local", "GOPROXY": "off"}


def script(name):
    return os.path.join(HERE, name)


def field_value(text, field):
    """从输出里取 `field=<整数>`；按行找、要求前面是行首或空格，避免子串误命中。"""
    pat = re.compile("(^| )" + re.escape(field) + "=([0-9]+)")
    for line in text.splitlines():
        m = pat.search(line.strip())
        if m:
            return int(m.group(2))
    return None


def parse_codes(out):
    """从 audit / check_links 的输出里抽出 (key, code) 对。"""
    seen = collections.defaultdict(set)
    for line in out.splitlines():
        line = line.strip()
        if " :: " not in line or line.startswith(("articles", "by_kind", "links_checked")):
            continue
        code, rest = line.split(" :: ", 1)
        seen[rest.split(" :: ")[0]].add(code)
    for line in out.splitlines():
        m = re.match(r"^\s*(BROKEN|UNMAPPED)\s+(\S+)\s+->\s+(.*)$", line)
        if m:
            seen[m.group(2)].add(m.group(1))
    return {k: sorted(v) for k, v in seen.items()}


def summary_line(out, keys):
    """按前缀找汇总行；hugo 的表格行带缩进与制表符，所以先 strip 再比。"""
    for line in out.splitlines():
        s = line.strip()
        if any(s.startswith(k) for k in keys):
            return s
    return ""


def hugo_pages(out):
    """从 hugo 输出里抠 Pages / Static files 两个数（它的表格是 ` Pages  │ 197`）。"""
    got = {}
    for line in out.splitlines():
        m = re.match(r"^\s*(Pages|Static files|Non-page files)\s*[│|]\s*(\d+)", line)
        if m:
            got[m.group(1)] = m.group(2)
    return " ".join("%s=%s" % (k, got[k]) for k in ("Pages", "Static files") if k in got)


def gates(args):
    """跑全部门，返回 [(名称, 类别, 状态, 摘要)]。"""
    rows = []
    site = os.path.abspath(args.site)

    if args.hugo and not args.skip_build:
        env = dict(HUGO_ENV)
        if args.go_bin:
            env["PATH"] = os.path.abspath(args.go_bin) + os.pathsep + os.environ.get("PATH", "")
        rc, out = run([args.hugo, "--cleanDestinationDir"], cwd=site, extra_env=env)
        err = len(re.findall(r"ERROR", out))
        detail = "%s ERROR=%d rc=%d" % (hugo_pages(out) or "no-pages-line", err, rc)
        if 'binary with name "go" not found' in out:
            detail += "；缺 go：Hugo 解析本地主题模块要调用 go，用 --go-bin <go的bin目录> 指定"
        elif "extended" in out.lower() and rc != 0:
            detail += "；疑似用了非 Extended 版 Hugo（主题要 SCSS 编译）"
        rows.append(("hugo build", "BUILD", "PASS" if rc == 0 and err == 0 else "FAIL", detail))
    else:
        rows.append(("hugo build", "BUILD", "SKIP", "未给 --hugo 或 --skip-build；链接判据需要 public/"))

    if os.path.isfile(script("matrix_check.py")) and args.src:
        cmd = [sys.executable, script("matrix_check.py"), "--matrix", args.matrix, "--src", args.src]
        for p in args.prefix or []:
            cmd += ["--prefix", p]
        for p in args.skip_prefix or []:
            cmd += ["--skip-prefix", p]
        rc, out = run(cmd)
        rows.append(("matrix_check", "AUTO", "PASS" if rc == 0 else "FAIL",
                     summary_line(out, ("categories=", "FAIL", "Traceback")) or "rc=%d" % rc))
    else:
        rows.append(("matrix_check", "AUTO", "SKIP",
                     "缺 scripts/matrix_check.py 或未给 --src"))

    cmd = [sys.executable, script("audit_structure.py"), "--site", site,
           "--matrix", args.matrix, "--min-lines", str(args.min_lines), "--scratch", args.scratch,
           "--mode", args.mode]
    if args.report:
        cmd += ["--report", args.report + ".audit.md"]
    rc, out = run(cmd)
    rows.append(("audit_structure", "AUTO", "PASS" if rc == 0 else "FAIL",
                 summary_line(out, ("articles=", "FAIL", "Traceback")) or "rc=%d" % rc))

    cmd = [sys.executable, script("check_links.py"), "--site", site]
    rc, out = run(cmd)
    rows.append(("check_links", "AUTO", "PASS" if rc == 0 else ("FAIL" if rc == 1 else "SKIP"),
                 summary_line(out, ("links_checked=", "FAIL", "Traceback")) or "rc=%d" % rc))

    rc, out = run([sys.executable, script("validate_mermaid.py"), "--site", site, "--selftest",
                   "--out", os.path.join(tempfile.gettempdir(), "replicate-mermaid-harness")])
    blocks = summary_line(out, ("mode=", "FAIL"))
    rows.append(("validate_mermaid", "MANUAL", "GENERATED" if rc == 0 else "FAIL",
                 (blocks + "；按脚本输出的三步在浏览器里读回 REAL_FAIL").strip()))

    if args.src and os.path.isfile(script("check_coverage.py")):
        cmd = [sys.executable, script("check_coverage.py"), "--site", site,
               "--matrix", args.matrix, "--src", args.src, "--worst", "5",
               "--min-lines", str(args.min_lines)]
        for p in args.prefix or []:
            cmd += ["--prefix", p]
        for p in args.skip_prefix or []:
            cmd += ["--skip-prefix", p]
        if args.gate:
            cmd += ["--gate", str(args.gate)]
        rc, out = run(cmd)
        rows.append(("check_coverage", "AUTO", "PASS" if rc == 0 else "FAIL",
                     summary_line(out, ("triage_", "gate=", "FAIL", "Traceback")) or "rc=%d" % rc))
    else:
        rows.append(("check_coverage", "AUTO", "SKIP", "未给 --src"))

    if os.path.isfile(script("picture_map.py")) and args.src:
        cmd = [sys.executable, script("picture_map.py"), "--matrix", args.matrix,
               "--src", args.src, "--site", site]
        for p in args.prefix or []:
            cmd += ["--prefix", p]
        for p in args.skip_prefix or []:
            cmd += ["--skip-prefix", p]
        rc, out = run(cmd)
        rows.append(("picture_map", "AUTO", "PASS" if rc == 0 else "FAIL",
                     summary_line(out, ("articles=", "FAIL", "Traceback")) or "rc=%d" % rc))
    return rows


def build_stub_public(root, skip_names):
    """按 check_links 的 URL 规则给夹具造一份最小 public/，让链接判据可离线自证。"""
    content = os.path.join(root, "content")
    pub = os.path.join(root, "public")
    made = 0
    for dp, _, fns in os.walk(content):
        for f in fns:
            if not f.endswith(".md") or f in skip_names:
                continue
            rel = os.path.relpath(os.path.join(dp, f), content).replace(os.sep, "/")
            parts = rel.split("/")
            if parts[-1] in ("_index.md", "index.md"):
                parts = parts[:-1]
            else:
                parts[-1] = re.sub(r"\.md$", "", parts[-1])
            parts = [p.lower() for p in parts]
            target = os.path.join(pub, *parts) if parts else pub
            os.makedirs(target, exist_ok=True)
            io.open(os.path.join(target, "index.html"), "w", encoding="utf-8", newline="\n").write(
                "<!doctype html><title>stub</title>\n")
            made += 1
    return made


def selftest():
    if not os.path.isdir(FIXTURES):
        print("SELFTEST_INVALID 缺夹具目录 %s" % FIXTURES)
        return 1
    tmp = tempfile.mkdtemp(prefix="replicate-selftest-")
    ok = True
    try:
        site = os.path.join(tmp, "site")
        shutil.copytree(os.path.join(FIXTURES, "site"), site)
        for jf in sorted(os.listdir(FIXTURES)):
            if jf.endswith(".json"):
                shutil.copyfile(os.path.join(FIXTURES, jf), os.path.join(tmp, jf))
        shutil.copytree(os.path.join(FIXTURES, "src"), os.path.join(tmp, "src"))
        exp = json.load(io.open(os.path.join(FIXTURES, "expected.json"), encoding="utf-8"))
        matrix = os.path.join(tmp, "matrix.json")

        made = build_stub_public(site, {"unmapped.md"})
        print("stub_public_pages=%d（unmapped.md 故意不造，用来触发 UNMAPPED）" % made)

        rc, out = run([sys.executable, script("audit_structure.py"), "--site", site,
                       "--matrix", matrix, "--min-lines", str(exp["min_lines"])])
        obs = parse_codes(out)
        obs_nz = {k: v for k, v in obs.items() if v}
        exp_nz = {k: sorted(v) for k, v in exp["audit"].items() if v}
        silent = sorted(k for k, v in exp["audit"].items() if not v)
        noisy = [k for k in silent if obs.get(k)]
        mism = sorted(k for k in set(obs_nz) | set(exp_nz) if obs_nz.get(k, []) != exp_nz.get(k, []))
        codes = sorted({c for v in obs_nz.values() for c in v})
        print("audit: rc=%d expected_keys=%d observed_keys=%d mismatch=%d 沉默样本=%d 其中被误报=%d"
              % (rc, len(exp_nz), len(obs_nz), len(mism), len(silent), len(noisy)))
        print("audit: 可达判据代码=%d" % len(codes))
        for k in mism:
            ok = False
            print("  MISMATCH %s observed=%s expected=%s" % (k, obs_nz.get(k), exp_nz.get(k, [])))
        for k in noisy:
            ok = False
            print("  FALSE_POSITIVE %s -> %s" % (k, ",".join(obs[k])))
        if rc == 0:
            ok = False
            print("  BAD 夹具站本该判失败，却退出 0")

        acopy = exp.get("audit_copy") or {}
        if acopy:
            rc, out = run([sys.executable, script("audit_structure.py"), "--site", site,
                           "--matrix", matrix, "--min-lines", str(exp["min_lines"]),
                           "--mode", "copy"])
            obs2 = {c for v in parse_codes(out).values() for c in v}
            absent = set(acopy.get("absent") or [])
            present = set(acopy.get("present") or [])
            leaked = sorted(absent & obs2)
            lost = sorted(present - obs2)
            print("audit --mode copy: rc=%d 文体判据沉默=%d/%d 结构判据仍生效=%d/%d"
                  % (rc, len(absent) - len(leaked), len(absent), len(present & obs2), len(present)))
            for c in leaked:
                ok = False
                print("  BAD copy 模式下文体判据仍在报：%s" % c)
            for c in lost:
                ok = False
                print("  BAD copy 模式下结构判据被误伤：%s" % c)
            if len(absent) + len(present) != len(codes):
                ok = False
                print("  BAD 两组判据之和 %d 对不上 rewrite 模式的可达判据代码总数 %d"
                      % (len(absent) + len(present), len(codes)))

        rc, out = run([sys.executable, script("check_links.py"), "--site", site])
        links = parse_codes(out)
        exp_links = {k: sorted(v) for k, v in exp["links"].items()}
        obs_links = {k: sorted(v) for k, v in links.items() if v}
        lmism = sorted(k for k in set(obs_links) | set(exp_links)
                       if obs_links.get(k, []) != exp_links.get(k, []))
        print("links: rc=%d %s" % (rc, summary_line(out, ("links_checked=",))))
        for k in lmism:
            ok = False
            print("  MISMATCH %s observed=%s expected=%s" % (k, obs_links.get(k, []), exp_links.get(k, [])))
        if rc == 0:
            ok = False
            print("  BAD 夹具站本该有断链，却退出 0")

        rc, out = run([sys.executable, script("fetch_source.py"), "--selftest"])
        st = "SELFTEST_PASS" in out
        print("fetch_source --selftest: rc=%d %s" % (rc, "PASS" if st else "FAIL"))
        if not st or rc != 0:
            ok = False

        mmjs = os.path.join(SKILL, "assets", "theme", "oink-main", "oink-main",
                            "assets", "third_party", "mermaid", "mermaid.min.js")
        cmd = [sys.executable, script("validate_mermaid.py"), "--site", site, "--selftest",
               "--out", os.path.join(tmp, "harness")]
        if os.path.isfile(mmjs):
            cmd += ["--mermaid-js", mmjs]
        rc, out = run(cmd)
        bj = os.path.join(tmp, "harness", "blocks.json")
        n = -1
        if os.path.isfile(bj):
            blocks = json.load(io.open(bj, encoding="utf-8"))
            n = len(blocks)
            st_ok = sum(1 for b in blocks if b["file"] == "SELFTEST") == 2
        else:
            st_ok = False
        print("validate_mermaid 生成解析台: rc=%d blocks=%d 注入好坏各一=%s（真解析仍需浏览器，属 MANUAL）"
              % (rc, n, st_ok))
        if rc != 0 or not st_ok:
            ok = False

        srcdir = os.path.join(tmp, "src")
        mexp = exp.get("matrix") or {}
        prefixes = mexp.get("prefixes") or ["4x=docs"]
        if os.path.isfile(script("matrix_check.py")) and mexp:
            for label, key in (("绿路", "ok"), ("红路", "bad")):
                spec = mexp.get(key) or {}
                mfile = os.path.join(tmp, spec.get("matrix_file", "matrix.json"))
                cmd = [sys.executable, script("matrix_check.py"), "--matrix", mfile, "--src", srcdir]
                for pf in prefixes:
                    cmd += ["--prefix", pf]
                rc, out = run(cmd)
                summ = summary_line(out, ("categories=", "FAIL", "Traceback"))
                codes = sorted({m.group(2) for m in re.finditer(r"^\s*(.+?) :: ([A-Z_]+) :: ", out, re.M)})
                print("matrix_check %s: rc=%d codes=%d %s" % (label, rc, len(codes), summ))
                want_rc = spec.get("exit")
                if want_rc is not None and rc != want_rc:
                    ok = False
                    print("  BAD %s 期望退出码 %s，实际 %d" % (label, want_rc, rc))
                want_codes = spec.get("codes")
                if want_codes:
                    miss = sorted(set(want_codes) - set(codes))
                    if miss:
                        ok = False
                        print("  BAD %s 这些判据没被触发：%s" % (label, ",".join(miss)))
                for field in ("UNCOVERED", "NONEXISTENT", "DUPLICATED", "same_name_pairs",
                              "identical", "differing", "per_article_pairs"):
                    if field in spec:
                        target = spec[field]
                        m = field_value(out, field)
                        if m is None or m != target:
                            ok = False
                            print("  BAD %s %s 期望 %s，实际 %s"
                                  % (label, field, target, "缺失" if m is None else m))
        else:
            ok = False
            print("matrix_check: BAD 脚本或夹具契约缺失")

        pexp = exp.get("picture") or {}
        if os.path.isfile(script("picture_map.py")) and pexp:
            cmd = [sys.executable, script("picture_map.py"),
                   "--matrix", os.path.join(tmp, pexp.get("matrix_file", "matrix_ok.json")),
                   "--src", srcdir, "--site", site]
            for pf in prefixes:
                cmd += ["--prefix", pf]
            rc, out = run(cmd)
            summ = summary_line(out, ("articles=", "FAIL", "Traceback"))
            print("picture_map: rc=%d %s" % (rc, summ))
            if rc != pexp.get("exit", 0):
                ok = False
                print("  BAD picture_map 退出码 %d != %s" % (rc, pexp.get("exit", 0)))
            for field in ("refs", "mapped", "missing_in_static"):
                if field in pexp:
                    target = pexp[field]
                    m = field_value(summ, field)
                    if m is None or m != target:
                        ok = False
                        print("  BAD picture_map %s 期望 %s，实际 %s"
                              % ("picture_map", field, target, "缺失" if m is None else m))
        else:
            print("picture_map: SKIP 脚本或夹具契约缺失")

        cexp = exp.get("coverage") or {}
        if os.path.isfile(script("check_coverage.py")) and cexp:
            cfile = os.path.join(tmp, cexp.get("matrix_file", "matrix_scope.json"))
            tag = cexp.get("skip_tag", "local")
            base = [sys.executable, script("check_coverage.py"), "--site", site,
                    "--matrix", cfile, "--src", srcdir, "--min-lines", str(exp["min_lines"])]
            for pf in prefixes:
                base += ["--prefix", pf]
            rc, out = run(base)
            hard = cexp.get("without_skip") or {}
            hit = hard.get("needle", "") in out
            print("check_coverage 未声明树外前缀: rc=%d 命中「%s」=%s" % (rc, hard.get("needle", ""), hit))
            if rc != hard.get("exit", 2) or not hit:
                ok = False
                print("  BAD 期望退出 %s 且点名未知前缀，实际 rc=%d hit=%s" % (hard.get("exit", 2), rc, hit))
            rc, out = run(base + ["--skip-prefix", tag])
            summ = summary_line(out, ("triage_", "FAIL", "Traceback"))
            print("check_coverage 声明 --skip-prefix %s: rc=%d %s" % (tag, rc, summ))
            soft = cexp.get("with_skip") or {}
            if rc != soft.get("exit", 0):
                ok = False
                print("  BAD 期望退出 %s，实际 %d" % (soft.get("exit", 0), rc))
            for field in ("rows", "error_rows", "out_of_scope"):
                if field in soft:
                    m = field_value(summ, field)
                    if m is None or m != soft[field]:
                        ok = False
                        print("  BAD check_coverage %s 期望 %s，实际 %s"
                              % (field, soft[field], "缺失" if m is None else m))
            if os.path.isfile(script("matrix_check.py")):
                mb = [sys.executable, script("matrix_check.py"), "--matrix", cfile, "--src", srcdir]
                for pf in prefixes:
                    mb += ["--prefix", pf]
                rc, out = run(mb)
                kinds = summary_line(out, ("SCHEMA=", "FAIL", "Traceback"))
                nb = field_value(kinds, "BAD_PREFIX")
                print("matrix_check 未声明树外前缀: rc=%d BAD_PREFIX=%s" % (rc, nb))
                if not nb:
                    ok = False
                    print("  BAD 期望 BAD_PREFIX 报红（防前缀写错的闸门），实际 %s" % nb)
                rc, out = run(mb + ["--skip-prefix", tag])
                kinds = summary_line(out, ("SCHEMA=", "FAIL", "Traceback"))
                summ = summary_line(out, ("categories=", "FAIL", "Traceback"))
                nb2 = field_value(kinds, "BAD_PREFIX")
                oos = field_value(summ, "out_of_scope")
                print("matrix_check 声明 --skip-prefix %s: BAD_PREFIX=%s out_of_scope=%s"
                      % (tag, nb2, oos))
                if nb2 != 0 or oos != soft.get("out_of_scope", 1):
                    ok = False
                    print("  BAD 期望 BAD_PREFIX=0 out_of_scope=%s，实际 %s/%s"
                          % (soft.get("out_of_scope", 1), nb2, oos))
        else:
            print("check_coverage: SKIP 脚本或夹具契约缺失")

        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        if ok:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print("保留夹具副本供排查：%s" % tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--matrix")
    ap.add_argument("--src")
    ap.add_argument("--prefix", action="append", default=[])
    ap.add_argument("--skip-prefix", action="append", default=[],
                    help="声明这些 tag 的源不在上游文档树内（如 local: 指向同级示例工程），"
                         "透传给 check_coverage 与 picture_map，单独计入 out_of_scope")
    ap.add_argument("--min-lines", type=int, default=260,
                    help="同时用于 audit_structure 的 TOO_SHORT 与 check_coverage 的「未写」判定")
    ap.add_argument("--mode", choices=("rewrite", "copy"), default="rewrite",
                    help="Step 0 由用户拍板的内容形态：rewrite = 按规范重写（默认，全部判据生效）；"
                         "copy = 完整复制原文，audit_structure 跳过 10 类文体判据")
    ap.add_argument("--scratch", default="_work")
    ap.add_argument("--gate", type=float, default=0.0)
    ap.add_argument("--hugo")
    ap.add_argument("--go-bin", help="go 可执行文件所在目录；工具链没进 PATH 时用它让 Hugo 能解析本地主题模块")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if not a.site or not a.matrix:
        print("FAIL 需要 --site 与 --matrix（或改用 --selftest）")
        sys.exit(2)

    rows = gates(a)
    width = max(len(r[0]) for r in rows)
    print("%-*s  %-6s  %-9s  %s" % (width, "判据", "类别", "状态", "摘要"))
    for name, kind, status, detail in rows:
        print("%-*s  %-6s  %-9s  %s" % (width, name, kind, status, detail))
    fails = [r for r in rows if r[2] == "FAIL"]
    manuals = [r for r in rows if r[2] in ("MANUAL", "GENERATED")]
    print("FAIL=%d MANUAL=%d PASS=%d SKIP=%d"
          % (len(fails), len(manuals), sum(1 for r in rows if r[2] == "PASS"),
             sum(1 for r in rows if r[2] == "SKIP")))
    if manuals:
        print("提醒：MANUAL 项没有结论，别把它当通过——mermaid 要在浏览器里读回 REAL_FAIL=0。")
    if a.report:
        with io.open(a.report, "w", encoding="utf-8", newline="\n") as f:
            f.write("# 验收汇总\n\n| 判据 | 类别 | 状态 | 摘要 |\n|---|---|---|---|\n")
            for name, kind, status, detail in rows:
                f.write("| `%s` | %s | %s | %s |\n" % (name, kind, status, detail.replace("|", "/")))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
