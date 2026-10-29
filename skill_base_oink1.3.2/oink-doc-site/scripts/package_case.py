"""打包实验验证案例：cases/<主题>/<案例>/ → 最小完整的 zip + static 发布副本。

用法：
  python package_case.py --site <站点目录> --theme <主题> --case <案例目录名> --init
  python package_case.py --site <站点目录> --theme <主题> --case <案例目录名> [--max-file-kb 10240]
  python package_case.py --selftest

退出码：0 = 打包成功且案例判据全绿；1 = 手册/内容不合格或案例判据有红；2 = 用法错。

顺序固定为五步，缺一步都不算完成：
  1) --init 建 cases/<主题>/<案例>/，写 .gitignore 基线与手册骨架
  2) 填手册（8 个小节）、放案例脚本与必要数据
  3) 本脚本按 .gitignore + 硬排除打 zip，并同步 static/cases/<主题>/<案例>.zip
  4) 在用到它的 content/**/*.md 里加真实 Markdown 下载链接
  5) hugo 重构建后跑 check_cases.py，必须 problems=0

最小完整：依赖目录（node_modules、__pycache__、.venv）、构建产物（dist、build、target）、
系统垃圾与密钥文件一律不进包；密钥与超限文件直接拒绝打包，不是静默剔除——
静默剔除会让作者以为包里全了。
"""

import argparse
import io
import os
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import check_cases  # noqa: E402

SKILL = os.path.dirname(HERE)
TEMPLATE = os.path.join(SKILL, "assets", "templates", "case-README.md")


def init_case(site, theme, case):
    p = check_cases.case_paths(site, theme, case)
    os.makedirs(os.path.join(p["dir"], "data"), exist_ok=True)
    made = []
    if not os.path.isfile(p["ignore"]):
        with io.open(p["ignore"], "w", encoding="utf-8", newline="\n") as f:
            f.write(check_cases.BASELINE_IGNORE)
        made.append(".gitignore")
    if os.path.isfile(p["manual"]):
        print("INIT_SKIP 手册已存在：%s" % check_cases.rel(site, p["manual"]))
    else:
        text = io.open(TEMPLATE, encoding="utf-8").read()
        text = text.replace("【案例名】", case).replace("【主题目录名】", theme)
        with io.open(p["manual"], "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        made.append("README.md")
    print("INIT_CREATED %s -> %s" % (p["url"].rsplit("/", 1)[0] + "/" + case + "/",
                                     "、".join(made) if made else "无（已存在）"))


def pack(site, theme, case, to_static=True, max_file_kb=10240):
    site = os.path.abspath(site)
    p = check_cases.case_paths(site, theme, case)
    if not os.path.isdir(p["dir"]):
        raise OSError("无案例目录：%s（先跑 --init）" % check_cases.rel(site, p["dir"]))
    problems = check_cases.manual_problems(site, theme, case)
    if problems:
        for code, target, detail in problems:
            print("  %s %s：%s" % (code, target, detail))
        raise OSError("手册不合格，拒绝打包：%s" % p["url"])

    files, dropped = check_cases.iter_files(p["dir"])
    if not files:
        raise OSError("案例目录是空的：%s" % check_cases.rel(site, p["dir"]))

    secrets = [r for r in files if check_cases.secret_hit(r)]
    if secrets:
        raise OSError("包里有疑似密钥文件，拒绝打包：%s（删掉，或改成 .env.example 之类的脱敏样本）"
                      % "、".join(secrets[:5]))
    big = [(r, os.path.getsize(os.path.join(p["dir"], r.replace("/", os.sep)))) for r in files
           if os.path.getsize(os.path.join(p["dir"], r.replace("/", os.sep))) > max_file_kb * 1024]
    if big:
        raise OSError("单文件超过 --max-file-kb=%d：%s（这类产物写「再生成命令」，不要进包）"
                      % (max_file_kb, "、".join("%s=%d" % (n, s) for n, s in big[:3])))

    os.makedirs(os.path.dirname(p["zip"]), exist_ok=True)
    with zipfile.ZipFile(p["zip"], "w", zipfile.ZIP_DEFLATED) as z:
        for r in files:
            z.write(os.path.join(p["dir"], r.replace("/", os.sep)), "%s/%s" % (case, r))
    print("package_case -> %s bytes=%d entries=%d excluded=%d"
          % (check_cases.rel(site, p["zip"]), os.path.getsize(p["zip"]), len(files), len(dropped)))
    if dropped:
        print("  excluded: %s" % "、".join(dropped[:6]) + ("…" if len(dropped) > 6 else ""))

    if to_static:
        os.makedirs(os.path.dirname(p["static"]), exist_ok=True)
        shutil.copyfile(p["zip"], p["static"])
        print("static -> %s bytes=%d"
              % (check_cases.rel(site, p["static"]), os.path.getsize(p["static"])))
    else:
        print("static -> 跳过（--no-static；发布副本缺失会被 check_cases 判 NO_STATIC_ZIP）")
    return p["zip"], files, dropped


def report_cases(site, max_file_kb):
    try:
        problems, stats = check_cases.check(site, max_file_kb)
    except OSError as e:
        print("check_cases SKIP %s" % e)
        return 0
    print("check_cases cases=%d doc_links=%d public=%s problems=%d"
          % (stats["cases"], stats["doc_links"], stats["public"], len(problems)))
    for code, target, detail in problems[:20]:
        print("  %s %s：%s" % (code, target, detail))
    return len(problems)


def selftest():
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-pack-", dir=os.path.abspath(root))
    ok = True
    try:
        theme, case = "05-net", "mtu-probe"
        site = os.path.join(tmp, "site")
        os.makedirs(os.path.join(site, "content", "docs"), exist_ok=True)
        cdir = os.path.join(site, "cases", theme, case)

        init_case(site, theme, case)
        manual = os.path.join(cdir, "README.md")
        if not (os.path.isfile(manual) and os.path.isfile(os.path.join(cdir, ".gitignore"))):
            ok = False
            print("SELFTEST_INVALID --init 没建出手册或 .gitignore")
        if not os.path.isfile(TEMPLATE):
            ok = False
            print("SELFTEST_INVALID 缺手册模板 %s" % TEMPLATE)
        try:
            pack(site, theme, case)
            ok = False
            print("SELFTEST_INVALID 占位手册竟然打包成功")
        except OSError as e:
            print("placeholder manual blocked: %s" % str(e)[:56])

        with io.open(manual, "w", encoding="utf-8", newline="\n") as f:
            f.write(check_cases.GOOD_MANUAL)
        with io.open(os.path.join(cdir, "probe.cmd"), "w", encoding="utf-8", newline="\n") as f:
            f.write("ping -n 1 127.0.0.1\n")
        os.makedirs(os.path.join(cdir, "node_modules", "dep"), exist_ok=True)
        with io.open(os.path.join(cdir, "node_modules", "dep", "index.js"), "w", encoding="utf-8") as f:
            f.write("module.exports = 1\n")
        os.makedirs(os.path.join(cdir, "__pycache__"), exist_ok=True)
        with io.open(os.path.join(cdir, "__pycache__", "x.pyc"), "wb") as f:
            f.write(b"\x00\x01")
        with io.open(os.path.join(cdir, "run.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("round-trip 12 ms\n")

        zp, files, dropped = pack(site, theme, case)
        entries = check_cases.zip_entries(zp)
        want = ["%s/%s" % (case, r) for r in files]
        kept_log = "%s/run.log" % case in entries
        deps_out = not any("node_modules" in e or "__pycache__" in e for e in entries)
        print("pack: entries=%d excluded=%d(node_modules+__pycache__) log_kept=%s"
              % (len(entries), len(dropped), kept_log))
        if entries != want or not deps_out or not kept_log:
            ok = False
            print("SELFTEST_INVALID 包内容不对：%s" % entries)

        with io.open(os.path.join(cdir, ".env"), "w", encoding="utf-8", newline="\n") as f:
            f.write("TOKEN=abc\n")
        try:
            pack(site, theme, case)
            ok = False
            print("SELFTEST_INVALID 密钥文件竟然打包成功")
        except OSError as e:
            print("secret blocked: %s" % str(e)[:56])
        os.remove(os.path.join(cdir, ".env"))

        with io.open(os.path.join(cdir, "big.bin"), "wb") as f:
            f.write(b"0" * 4096)
        try:
            pack(site, theme, case, max_file_kb=1)
            ok = False
            print("SELFTEST_INVALID 超限文件竟然打包成功")
        except OSError as e:
            print("oversize blocked: %s" % str(e)[:56])
        os.remove(os.path.join(cdir, "big.bin"))

        check_cases.write(os.path.join(site, "content", "docs", "net.md"),
                          "[mtu-probe.zip](/cases/05-net/mtu-probe.zip)\n")
        zp, files, _ = pack(site, theme, case)
        os.makedirs(os.path.join(site, "public", "cases", theme), exist_ok=True)
        shutil.copyfile(zp, os.path.join(site, "public", "cases", theme, case + ".zip"))
        if report_cases(site, 10240) != 0:
            ok = False
            print("SELFTEST_INVALID 四方齐全却没判绿")

        os.remove(os.path.join(site, "static", "cases", theme, case + ".zip"))
        if report_cases(site, 10240) == 0:
            ok = False
            print("SELFTEST_INVALID 删掉 static 副本却没报红")
        else:
            print("static deleted -> 判据会红（符合预期）")
        pack(site, theme, case)

        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--theme")
    ap.add_argument("--case")
    ap.add_argument("--init", action="store_true", help="只建案例骨架：.gitignore + 手册模板")
    ap.add_argument("--no-static", action="store_true", help="只打 cases/ 下的 zip，不同步 static 副本")
    ap.add_argument("--max-file-kb", type=int, default=10240, help="单文件上限，超过拒绝打包")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.site and a.theme and a.case):
        print("FAIL 需要 --site --theme --case（或 --selftest）")
        sys.exit(2)
    if a.init:
        init_case(os.path.abspath(a.site), a.theme, a.case)
        sys.exit(0)
    try:
        pack(a.site, a.theme, a.case, to_static=not a.no_static, max_file_kb=a.max_file_kb)
    except (OSError, ValueError) as e:
        print("FAIL %s" % e)
        sys.exit(1)
    sys.exit(1 if report_cases(a.site, a.max_file_kb) else 0)


if __name__ == "__main__":
    main()
