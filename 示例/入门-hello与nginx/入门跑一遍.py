# -*- coding: utf-8 -*-
"""入门跑一遍：hello-world 与 nginx 各跑一次，并且**每条判据都会自己红**。

这是 [/docs/01-基础认知/第一次动手/第一次运行容器与图形化工具/](/docs/01-基础认知/第一次动手/第一次运行容器与图形化工具/)
那篇 1.3 的产出物。它和「跟着敲一遍」的区别只有一件事：**每个结论都由脚本断言，
而且断言先被喂坏样本证明它会红**（`--selftest`），否则一条永远为真的检查等于没检查。

用法：
    python 入门跑一遍.py --selftest   # 先跑这个：五条坏样本必须全被抓到
    python 入门跑一遍.py               # 再跑主流程，读 checks=… FAIL=0

设计约束（写在代码里而不是写在注释里的原因：它们决定了判据能不能红）：
  - 每条「成功」判据都要能被同一条代码判成「失败」，所以检查函数都收参数，不写死常量；
  - 「变化真的发生了」类判据要成对取数（访问前 / 访问后），只取一次不算；
  - 收尾只按**记下的名字**删，不用任何宽口清理；端口用 bind+netstat 现挑，不猜。
"""
import argparse
import io
import os
import re
import socket
import subprocess
import sys
import time

IMAGE_HELLO = "hello-world"
IMAGE_WEB = "nginx:1.27-alpine"
NAME = "kb31_intro_web"
MARK = "Hello from Docker!"
UA = "kb31-intro-probe"

CHECKS = []      # (编号, 说明, 结果 bool/None)  None = 需人工
FAILS = []


def sh(args, timeout=240):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or ""), (p.stderr or "")


def check(cid, desc, ok):
    CHECKS.append((cid, desc, ok))
    if ok is False:
        FAILS.append(cid)
    tag = "PASS" if ok is True else ("MANUAL" if ok is None else "FAIL")
    print(f"  [{tag}] {cid:4s} {desc}")


def pick_port(start=18901, tries=80, taken=()):
    ns = sh(["netstat", "-ano"])[1]
    for p in range(start, start + tries):
        if p in taken or f":{p}" in ns:
            continue
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
            except OSError:
                continue
        return p
    raise RuntimeError("没有可用端口")


# ---------- 可复用的检查函数（坏样本就靠喂不同参数造出来） ----------

def expect_marker(text, marker):
    """输出里必须出现指定标记。喂一个不存在的 marker 就必然红。"""
    return marker in text


def expect_http(url, want_code="200", timeout=10):
    rc, so, _ = sh(["curl", "-s", "-o", "/dev/null", "-m", str(timeout), "-w", "%{http_code}", url])
    return so.strip() == want_code


def log_line_delta(before, after, need=1):
    """访问前后各数一次日志行数，增量必须 >= need。两次相同就红。"""
    return (after - before) >= need


def expect_unreachable(url, timeout=6):
    """停掉之后要真的连不上：没有 HTTP 码才算对。"""
    rc, so, _ = sh(["curl", "-s", "-o", "/dev/null", "-m", str(timeout), "-w", "%{http_code}", url])
    return so.strip() in ("", "000")


def expect_split(err_text, out_text, marker):
    """带版本号的自报行只该在 stderr，access log 只该在 stdout。

    注意口径：`nginx/` 这个词在 stdout 里也会出现（入口脚本打印 /etc/nginx/conf.d/default.conf），
    所以判据必须钉在「nginx/\\d+\\.\\d+」这个形状上，而不是「有没有 nginx/」。
    """
    ver_in_err = bool(re.search(r"nginx/\d+\.\d+", err_text))
    ver_in_out = bool(re.search(r"nginx/\d+\.\d+", out_text))
    return ver_in_err and not ver_in_out and (marker in out_text) and (marker not in err_text)


def expect_absent(items):
    return len([x for x in items if x.strip()]) == 0


def selftest():
    print("== 先证明这些判据会红（五条坏样本）==")
    caught = 0
    bad1 = expect_marker(MARK, "Hello from Mars")
    print(f"  坏样本 1 标记写错 -> {'抓到' if not bad1 else '漏了'}（正样本同函数：{expect_marker(MARK, MARK)}）")
    caught += 0 if bad1 else 1
    dead = pick_port()
    bad2 = expect_http(f"http://127.0.0.1:{dead}/", want_code="200", timeout=3)
    print(f"  坏样本 2 没人监听的端口当成 200 -> {'抓到' if not bad2 else '漏了'}")
    caught += 0 if bad2 else 1
    bad3 = log_line_delta(7, 7)
    print(f"  坏样本 3 访问前后行数没变 -> {'抓到' if not bad3 else '漏了'}（正样本：{log_line_delta(7, 8)}）")
    caught += 0 if bad3 else 1
    bad4 = expect_absent([NAME, ""])
    print(f"  坏样本 4 残留列表里还留着名字 -> {'抓到' if not bad4 else '漏了'}（正样本：{expect_absent(['', ''])}）")
    caught += 0 if bad4 else 1
    # 把两条流对调喂进去：版本行跑到 stdout、access log 跑到 stderr，分流判据必须红
    bad5 = expect_split("172.17.0.1 GET / " + UA, "nginx/1.27.5 notice", UA)
    print(f"  坏样本 5 两个流对调 -> {'抓到' if not bad5 else '漏了'}"
          f"（正样本：{expect_split('nginx/1.27.5 notice', 'GET / ' + UA, UA)}）")
    caught += 0 if bad5 else 1
    ok = caught == 5
    print(f"SELFTEST={'PASS' if ok else 'FAIL'} 抓到 {caught}/5 条坏样本")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="只跑坏样本（五条），证明判据会红")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)

    print("先跑 --selftest 再看这里；下面每条 PASS 的前提是上面 4/4。")
    if not selftest():
        print("判据没被证明会红，主流程拒绝出绿。")
        sys.exit(1)
    print("")

    base = (len([x for x in sh(["docker", "ps", "-aq"])[1].split("\n") if x.strip()]),
            len([x for x in sh(["docker", "volume", "ls", "-q"])[1].split("\n") if x.strip()]),
            len([x for x in sh(["docker", "network", "ls", "-q"])[1].split("\n") if x.strip()]))
    print(f"开工基线 容器/卷/网络 = {base}")
    pre = sh(["docker", "ps", "-aq", "--filter", f"name={NAME}"])[1]
    check("C0", f"开工前 {NAME} 不存在", expect_absent(pre.split("\n")))

    rc, so, se = sh(["docker", "run", "--rm", IMAGE_HELLO])
    check("C1", f"{IMAGE_HELLO} 退出码为 0（rc={rc}）", rc == 0)
    check("C2", f"输出里有「{MARK}」", expect_marker(so, MARK))
    resid = sh(["docker", "ps", "-aq", "--no-trunc", "--filter", f"ancestor={IMAGE_HELLO}"])[1]
    check("C3", "--rm 跑完不留容器", expect_absent(resid.split("\n")))

    port = pick_port()
    url = f"http://127.0.0.1:{port}/"
    rc, cid, se = sh(["docker", "run", "-d", "--name", NAME, "-p", f"127.0.0.1:{port}:80", IMAGE_WEB])
    check("C4", f"起 nginx 在 127.0.0.1:{port}（rc={rc}）", rc == 0)
    st = sh(["docker", "ps", "--filter", f"name={NAME}", "--format", "{{.State}}"])[1].strip()
    check("C5", "ps 里它的 State 是 running", st == "running")

    ready = False
    for _ in range(15):
        if expect_http(url):
            ready = True
            break
        time.sleep(1)
    check("C6", "就绪探针拿到 HTTP 200", ready)

    rc, l0, e0 = sh(["docker", "logs", NAME])
    n0 = len([x for x in l0.split("\n") if "GET /" in x])
    sh(["curl", "-s", "-A", UA, "-m", "10", url])
    time.sleep(0.6)
    _, l1, e1 = sh(["docker", "logs", NAME])
    n1 = len([x for x in l1.split("\n") if "GET /" in x])
    check("C7", f"访问之后 access log 行数增加（{n0} -> {n1}）", log_line_delta(n0, n1))
    check("C8", "日志里能看到那次请求的 UA 标记", UA in l1)
    # 版本行不在 stdout 而在 stderr：nginx 把 notice/error 写 stderr，access log 写 stdout。
    # 只搜 stdout 的判据会永远读不到版本（本脚本第一次跑就在这一格红过）。
    both = l1 + "\n" + e1
    m = re.search(r"nginx/\d+\.\d+", both)
    check("C9", f"日志自报版本（{m.group(0) if m else '没读到'}，在 stderr 那一半）", bool(m))
    # 「stdout 里完全没有 nginx/ 这个词」是错的——入口脚本会打印 /etc/nginx/conf.d/default.conf。
    # 精确的口径是：**带版本号的自报行**只在 stderr，access log 只在 stdout。
    check("C9b", f"分流判据（版本行只在 stderr、access log 只在 stdout）：{expect_split(e1, l1, UA)}",
          expect_split(e1, l1, UA))

    rc, so, _ = sh(["docker", "stop", NAME], timeout=120)
    check("C10", "stop 返回容器名（rc=0）", rc == 0 and so.strip() == NAME)
    check("C11", "stop 之后端口连不上", expect_unreachable(url))
    state = sh(["docker", "ps", "-a", "--filter", f"name={NAME}", "--format", "{{.State}}"])[1].strip()
    check("C12", f"stop 后容器还在、状态是 exited（现读 {state}）", state == "exited")
    rc2, _, se2 = sh(["docker", "rm", "-f", NAME])
    check("C13", "rm 按名删掉", rc2 == 0)
    after = sh(["docker", "ps", "-aq", "--filter", f"name={NAME}"])[1]
    check("C14", "删后按名查为空", expect_absent(after.split("\n")))

    now = (len([x for x in sh(["docker", "ps", "-aq"])[1].split("\n") if x.strip()]),
           len([x for x in sh(["docker", "volume", "ls", "-q"])[1].split("\n") if x.strip()]),
           len([x for x in sh(["docker", "network", "ls", "-q"])[1].split("\n") if x.strip()]))
    check("C15", f"全量计数回到开工基线（{base} -> {now}）", now == base)
    check("C16", "浏览器里看到的那页 = curl 拿到的那页（人工）", None)

    auto = [c for c in CHECKS if c[2] is not None]
    manual = [c for c in CHECKS if c[2] is None]
    print(f"\n汇总：checks={len(CHECKS)} AUTO_PASS={len([c for c in auto if c[2]])} "
          f"MANUAL={len(manual)} FAIL={len(FAILS)}")
    if FAILS:
        print("FAIL_IDS=" + ",".join(FAILS))
        sys.exit(1)
    print("INTRO_PASS")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
