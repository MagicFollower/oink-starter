"""Harbor 本机部署的驱动脚本（真实案例，全部命令都在本机跑过）。

为什么用 Python 而不是 shell：这台机器上判据一律走 argv（MSYS 会改写容器内路径），
且官方 `prepare` 需要的挂载路径是 **Docker Desktop VM 里的 /data**，路径拼接错了不会报错、
只会安静地生成一份没用的配置。

六个子命令，一条命令只做一件事，便于逐步记录：
  cert      用一个临时容器在 VM 的 /data/harbor-certs 里生成自签 CA + 服务器证书（SAN 三项：localhost、host.docker.internal、127.0.0.1）
  config    在官方 harbor.yml.tmpl 上替换六个键，写出本机实参 harbor.yml
  prepare   复刻官方 prepare 的那一条 docker run（goharbor/prepare:v2.14.6），生成 common/ 与 docker-compose.yml
  up        docker compose up -d（读官方生成的那份 compose）
  status    组件容器健康 + /api/v2.0/health（带 -k 与不带 -k 各一次）
  verify    判据集：登录、建项目、push、pull、查仓库与制品、统计、匿名 V2
  trust     把 CA 落到本目录 certs/，并打印出厂 insecure 段与 certs.d 两条路各自的失败原文
"""
import argparse
import json
import os
import subprocess
import sys
import time

REG = "localhost:8443"
IMAGE = "goharbor/prepare:v2.14.6"
HERE = os.path.dirname(os.path.abspath(__file__))
YML = os.path.join(HERE, "harbor.yml")
TMPL = os.path.join(HERE, "官方安装包留档", "harbor.yml.tmpl")
ADMIN_PW = "Harbor12345"      # 演示值；真实部署改 harbor.yml 并同步这里

# config 子命令只替换这六个键（正则需要匹配官方模板里的原行），顺序无关
PATCH = {
    r"^hostname: ": "hostname: localhost",
    r"^  port: 80$": "  port: 8081",
    r"^  port: 443$": "  port: 8443",
    r"^  certificate: ": "  certificate: /data/harbor-certs/harbor.crt",
    r"^  private_key: ": "  private_key: /data/harbor-certs/harbor.key",
    r"^harbor_admin_password: ": "harbor_admin_password: " + ADMIN_PW,
}

# 写在 harbor.yml 顶部的说明，6 行（模板 339 行 + 6 = 345 行）
NOTE = (
    "# 本文件由 harborctl.py 的 config 子命令在官方 harbor.yml.tmpl（v2.14.6，发布日 2026-10-23）上逐行替换生成；\n"
    "#   改动仅限 PATCH 里列的六个键：hostname / http.port / https.port / https.certificate / https.private_key / harbor_admin_password\n"
    "# hostname 用 localhost 而不是 127.0.0.1：prepare 的配置校验硬拒 IP（原文 `ERROR:root:127.0.0.1 can not be the hostname`），\n"
    "#   而 localhost 能过；两者对 Windows 客户端与 VM 里的 daemon 都可解析，端口 8443 避开 443 被占与 IPv6 回环那对坑。\n"
    "# certificate/private_key 指向 /data/harbor-certs —— /data 是 Docker Desktop VM 里的目录，不是 Windows 路径。\n"
    "# data_volume 保持官方默认 /data；harbor_admin_password 沿用演示值（真实部署必须改）。\n"
)


def sh(args, tmo=1200, cwd=HERE):
    p = subprocess.run(list(args), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=tmo, cwd=cwd, env=dict(os.environ))
    out = ((p.stdout or "") + (p.stderr or "")).replace("\r", "")
    print("$ " + " ".join(args))
    return p.returncode, out


def tail(text, n=1):
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    return " | ".join(lines[-n:]) if lines else "(无输出)"


def cert():
    print("=== 1. 生成 CA 与服务器证书（写在 VM 的 /data/harbor-certs；ca.key 要留着，否则无法再签第二张）")
    san = "DNS:localhost,DNS:host.docker.internal,IP:127.0.0.1"
    rc, out = sh(["docker", "run", "--rm", "-v", "/data/harbor-certs:/certs", "alpine:3.20", "sh", "-c",
                  "apk add --no-cache openssl >/dev/null && cd /certs && "
                  "if [ ! -f ca.key ]; then openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes "
                  "-keyout ca.key -out ca.crt -subj '/CN=Harbor Demo CA' "
                  "-addext 'basicConstraints=critical,CA:TRUE'; fi && "
                  "openssl req -newkey rsa:2048 -nodes -keyout harbor.key -out harbor.csr -subj '/CN=localhost' && "
                  "printf 'subjectAltName=" + san + chr(92) + "n' > san.ext && "
                  "openssl x509 -req -in harbor.csr -CA ca.crt -CAkey ca.key -CAcreateserial "
                  "-out harbor.crt -days 825 -sha256 -extfile san.ext && rm -f harbor.csr san.ext && "
                  "chmod 644 harbor.crt ca.crt && "
                  "openssl x509 -in harbor.crt -noout -subject -issuer -ext subjectAltName"])
    print("   rc=%d %s" % (rc, out.replace(chr(10), " | ")[-260:]))
    return rc


def config():
    print("=== 2. 由官方模板生成本机 harbor.yml（只换六个键，其余键与注释原样保留）")
    if not os.path.isfile(TMPL):
        print("   缺官方模板：", TMPL)
        return 1
    import re
    src = open(TMPL, encoding="utf-8").read()
    hit = {}
    out = []
    for line in src.splitlines():
        for pat, new in PATCH.items():
            if re.match(pat, line):
                hit[pat] = hit.get(pat, 0) + 1
                line = new
                break
        out.append(line)
    body = NOTE + "\n".join(out) + "\n"
    open(YML, "w", encoding="utf-8", newline="\n").write(body)
    print("   模板 %d 行 -> harbor.yml %d 行；每个替换命中次数=%s" %
          (len(src.splitlines()), len(out), hit))
    miss = [p for p in PATCH if p not in hit]
    print("   没命中的替换：%s" % (miss or "无"))
    return 1 if miss else 0


def prepare():
    print("=== 3. 官方 prepare（复刻安装包里那两条：先 cp harbor.yml 到 input/，再跑 goharbor/prepare 容器）")
    os.makedirs(os.path.join(HERE, "input"), exist_ok=True)
    if not os.path.isfile(YML):
        print("   先跑 config")
        return 1
    # 官方 prepare 脚本第 12~30 行做的正是这件事：清空 input、把 harbor.yml 拷进去
    import shutil
    shutil.rmtree(os.path.join(HERE, "input"), ignore_errors=True)
    os.makedirs(os.path.join(HERE, "input"))
    shutil.copyfile(YML, os.path.join(HERE, "input", "harbor.yml"))
    print("   input/harbor.yml 就位（%d 字节）" % os.path.getsize(os.path.join(HERE, "input", "harbor.yml")))
    rc, out = sh(["docker", "run", "--rm",
                  "-v", os.path.join(HERE, "input") + ":/input",
                  "-v", "/data:/data",
                  "-v", HERE + ":/compose_location",
                  "-v", os.path.join(HERE, "common", "config") + ":/config",
                  "-v", "/:/hostfs/",
                  "--privileged", IMAGE, "prepare"], tmo=600)
    print("   rc=%d 尾部：%s" % (rc, tail(out, 3)))
    if rc == 0:
        print("   产物：docker-compose.yml %s 字节；common/config 下的目录：" %
              (os.path.getsize(os.path.join(HERE, "docker-compose.yml"))
               if os.path.isfile(os.path.join(HERE, "docker-compose.yml")) else "缺"))
        for root, dirs, _ in os.walk(os.path.join(HERE, "common")):
            if dirs:
                print("     ", os.path.relpath(root, HERE).replace("\\", "/"), "->", sorted(dirs))
    return rc


def up():
    print("=== 4. 起 Harbor（官方生成的 docker-compose.yml）")
    comp = os.path.join(HERE, "docker-compose.yml")
    if not os.path.isfile(comp):
        print("   还没有 docker-compose.yml，先跑 prepare")
        return 1
    # 显式给项目名：compose 默认用目录名当项目名，而本目录名含中文，
    # 网络与卷名前缀会带上非 ASCII，别处引用时容易踩编码坑
    rc, out = sh(["docker", "compose", "-p", "harbor", "-f", comp, "up", "-d"], tmo=3600)
    print("   rc=%d 尾部：%s" % (rc, tail(out, 3)))
    return rc


def status():
    print("=== 5. 组件状态与 API 健康")
    rc, out = sh(["docker", "ps", "--format", "{{.Names}} {{.Status}} {{.Image}}"])
    hb = [l for l in out.splitlines() if "harbor" in l]
    print("   Harbor 相关容器 %d 个：" % len(hb))
    for l in hb:
        print("     ", l[:110])
    time.sleep(2)
    rc, out = sh(["curl", "-sk", "-m", "10", "-w", "|http=%{http_code}", "https://%s/api/v2.0/health" % REG])
    print("   /api/v2.0/health（带 -k，未装 CA 时也能通）：", out[:200])
    rc, out = sh(["curl", "-s", "-m", "8", "-w", "|http=%{http_code}", "https://%s/api/v2.0/health" % REG])
    print("   同一个地址**不带 -k**：", out[:220])
    return 0


def trust():
    """本机实测结论：Windows 上这条路对带端口的仓库名走不通，daemon 侧也没有 /etc/docker 可写。
    所以 trust 子命令只做两件事：把 CA 落到本目录（供 --cacert 与浏览器用），并打印出厂的 insecure 段证明为什么。"""
    print("=== 6. CA 交付：写到本目录 + 解释为什么 certs.d 那两条路在本机都不通")
    os.makedirs(os.path.join(HERE, "certs"), exist_ok=True)
    rc, pem = sh(["docker", "run", "--rm", "-v", "/data/harbor-certs:/certs", "alpine:3.20",
                  "cat", "/certs/ca.crt"])
    if rc != 0:
        print("   取 CA 失败：", tail(pem, 2))
        return rc
    dst = os.path.join(HERE, "certs", "harbor-ca.crt")
    open(dst, "w", encoding="utf-8", newline="\n").write(pem)
    print("   CA 落到", dst, "（%d 字节）——给 curl --cacert、浏览器与 CI 用" % len(pem))
    rc, out = sh(["docker", "info", "--format", "{{json .RegistryConfig.InsecureRegistryCIDRs}}"])
    print("   出厂 insecure 段：", out, "← 所以 localhost:8443 的 push 根本不走证书校验")
    for name in (REG, "localhost!8443"):
        p = os.path.join(os.environ.get("USERPROFILE", ""), ".docker", "certs.d", name)
        try:
            os.makedirs(p, exist_ok=True)
            print("   试建 %s -> 成功（说明这个名字合法）" % name)
            os.rmdir(p)
        except Exception as e:
            print("   试建 %s -> %s: %s" % (name, type(e).__name__, str(e)[:64]))
    rc, out = sh(["wsl", "-d", "docker-desktop", "-u", "root", "sh", "-c",
                  "ls -d /etc/docker/certs.d 2>/dev/null || echo 'VM 里没有 /etc/docker'"], tmo=120)
    print("   VM 侧 daemon 的证书目录：", out.replace("\n", " ")[-90:])
    print("   本机客户端用 CA 直接验一次（不经 daemon）：")
    rc, out = sh(["curl", "-s", "--cacert", dst, "-m", "10", "-w", "|http=%{http_code}",
                  "https://127.0.0.1:8443/api/v2.0/health"])
    print("     curl --cacert 127.0.0.1 ->", out[:170])
    rc, out = sh(["curl", "-s", "-m", "10", "-w", "|http=%{http_code}", "https://localhost:8443/api/v2.0/health"])
    print("     同一个地址不带 CA ->", out[:170])
    return 0


def verify():
    print("=== 7. 判据：登录 → 建项目 → push → pull → 删除/扫描")
    base = "https://%s/api/v2.0" % REG
    rc, out = sh(["curl", "-s", "-m", "10", "-u", "admin:" + ADMIN_PW, base + "/health"])
    print("   不带 -k 的登录检查 rc=%d（Windows 上是 60 + schannel: SEC_E_UNTRUSTED_ROOT；"
          "这本身就是『daemon 不验、curl 验』的对照）" % rc)
    rc, out = sh(["curl", "-s", "-k", "-m", "10", "-u", "admin:" + ADMIN_PW, base + "/health"])
    print("   带 -k：", out[:150])
    proj = json.dumps({"project_name": "kbdemo", "registry_id": None,
                       "metadata": {"public": "true"}})
    open(os.path.join(HERE, "project.json"), "w", encoding="utf-8").write(proj)
    rc, out = sh(["curl", "-s", "-m", "15", "-k", "-u", "admin:" + ADMIN_PW,
                  "-X", "POST", "-H", "Content-Type: application/json",
                  "-o", "-", "-w", "|HTTP=%{http_code}",
                  "--data=@" + os.path.join(HERE, "project.json").replace("\\", "/"),
                  base + "/projects"], tmo=60)
    # curl 的 rc=0 只说明「请求发出去并收到了响应」，4xx 也是 0，所以必须打 HTTP 码
    print("   建项目 curl rc=%d 响应=%s" % (rc, tail(out, 2)[:200]))
    rc, out = sh(["curl", "-s", "-k", "-m", "10", "-D", "-", "-o", "NUL",
                  "https://%s/v2/" % REG], tmo=60)
    print("   匿名 /v2/（401 才是通的证明）：", out.replace("\r", "")[:260])
    tag = "%s/kbdemo/harbor-probe:1" % REG
    rc, out = sh(["docker", "tag", "alpine:3.20", tag], tmo=60)
    rc, out = sh(["docker", "push", tag], tmo=600)
    print("   push rc=%d 尾部=%s" % (rc, tail(out, 2)[:200]))
    rc, out = sh(["docker", "rmi", tag], tmo=60)
    rc, out = sh(["docker", "pull", tag], tmo=300)
    print("   删本地后 pull rc=%d 尾部=%s" % (rc, tail(out, 2)[:180]))
    # Harbor 2.14 的 API 是嵌套式：/projects/<项目>/repositories/<仓库名（不含项目前缀）>/artifacts
    # 曾经试过的 /repositories/kbdemo%2Fharbor-probe/artifacts 会先被解码回斜杠，再报
    # {"errors":[{"code":"NOT_FOUND","message":"path /api/v2.0/repositories/kbdemo/harbor-probe/artifacts was not found"}]}
    rc, out = sh(["curl", "-s", "-m", "12", "-k", "-u", "admin:" + ADMIN_PW,
                  base + "/projects/kbdemo/repositories"], tmo=60)
    print("   项目里的仓库：", out[:200])
    rc, out = sh(["curl", "-s", "-m", "12", "-k", "-u", "admin:" + ADMIN_PW,
                  base + "/projects/kbdemo/repositories/harbor-probe/artifacts"], tmo=60)
    print("   artifact 摘要：", out[:170])
    rc, out = sh(["curl", "-s", "-m", "12", "-k", "-u", "admin:" + ADMIN_PW, base + "/statistics"], tmo=60)
    print("   统计：", out[:170])
    rc, out = sh(["curl", "-s", "-k", "-m", "12", "https://%s/v2/kbdemo/harbor-probe/tags/list" % REG], tmo=60)
    print("   不带凭据直接走 OCI V2 列标签：", out[:150])

    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="status",
                    choices=["cert", "config", "prepare", "up", "status", "trust", "verify", "down"])
    a = ap.parse_args()
    fn = {"cert": cert, "config": config, "prepare": prepare, "up": up,
          "status": status, "trust": trust, "verify": verify}[a.cmd]
    if a.cmd == "down":
        rc, out = sh(["docker", "compose", "-p", "harbor", "-f", os.path.join(HERE, "docker-compose.yml"), "down"])
        print(tail(out, 3))
        return rc
    return fn()


if __name__ == "__main__":
    sys.exit(main() or 0)
