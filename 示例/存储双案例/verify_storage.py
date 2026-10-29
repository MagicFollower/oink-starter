"""存储双案例的判据脚本：逐条把 10-存储专题 正文里的说法在这台机器上验一遍。

用法：
    python verify_storage.py            # 先自证判据会红，再跑全部 12 条；任何一条红 → 退出码 1
    python verify_storage.py --selftest # 只跑坏样本：三条必须都被抓到

为什么要 --selftest：一条永远不会红的判据等于没有判据。这里刻意造三种错（把期望聚合改成不可能的值、
拿一只没有 tmpfs 的容器去验 tmpfs 判据、把挂载形态期望改成 99 条 bind），要求它们必须 FAIL。
只有坏样本全被抓到，主跑的 PASS 才有意义。

全程只读：唯一的"写"是在容器里往只读挂载试写一次（那正是被验的行为）。
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DBPW = 'KbSt#Test2026'
AGG_EXPECT = '5000\t10728165079651'   # 出厂基线：5000 行 + CRC32 聚合（down -v 后重新 up 应当复现）
PROBE_TEXT = 'probe-ok from ro-bind config'
BIG_SIZE = 1179648


def r(args, tmo=180):
    p = subprocess.run(args, capture_output=True, timeout=tmo, cwd=HERE)
    return p.returncode, ((p.stdout or b'').decode('utf-8', 'replace') +
                          (p.stderr or b'').decode('utf-8', 'replace')).strip()


def sql(q, target='kbst-db', tmo=180):
    p = subprocess.run(['docker', 'exec', '-e', 'MYSQL_PWD=' + DBPW, target, 'mysql', '-uroot', '-N', '-e', q],
                       capture_output=True, timeout=tmo, cwd=HERE)
    out = ((p.stdout or b'').decode('utf-8', 'replace') + (p.stderr or b'').decode('utf-8', 'replace')).strip()
    return '\n'.join([l for l in out.split('\n') if 'Warning' not in l])


def mounts_of(name):
    rc, o = r(['docker', 'inspect', '--format', '{{json .Mounts}}', name])
    try:
        return json.loads(o) or []
    except Exception:
        return []


# ---------------- 12 条判据：每条一个函数，返回 (是否通过, 读数) ----------------

def c01_running():
    a = r(['docker', 'inspect', '--format', '{{.State.Status}}', 'kbst-web'])[1]
    b = r(['docker', 'inspect', '--format', '{{.State.Status}}', 'kbst-db'])[1]
    h = r(['docker', 'inspect', '--format', '{{.State.Health.Status}}', 'kbst-db'])[1]
    return (a == 'running' and b == 'running' and h == 'healthy'), f'web={a} db={b} 健康={h}'


def c02_data_baseline(expect=None):
    o = sql('SELECT COUNT(*), SUM(CRC32(CONCAT(id,body,tag,crc))) FROM kbdb.t_note;')
    want = expect if expect is not None else AGG_EXPECT
    return o.split('\n')[0] == want, o.split('\n')[0]


def c03_mount_shape(over=None):
    want = over if over is not None else {'bind': 3, 'volume': 4}
    rows = []
    for c in ('kbst-web', 'kbst-db'):
        for m in mounts_of(c):
            rows.append((m['Type'], m.get('Name', ''), m['Destination']))
    tally = {}
    for t, _n, _d in rows:
        tally[t] = tally.get(t, 0) + 1
    return tally == want, f'共 {len(rows)} 条 {tally}（期望 {want}）'


def c04_fstype():
    m = r(['docker', 'exec', 'kbst-web', 'sh', '-c',
           'grep -E " /usr/share/nginx/html | /usr/share/nginx/html2 | /cache " /proc/mounts'])[1]
    ok = (' 9p ' in m and ' ext4 ' in m and ' tmpfs ' in m)
    return ok, m.replace('\n', ' | ')[:220]


def c05_same_volume_two_paths():
    o = r(['docker', 'exec', 'kbst-web', 'sh', '-c',
           'stat -c "%n dev=%D in=%i" /usr/share/nginx/html2 /probe/volume-on-missing-path /usr/share/nginx/html'])[1]
    d = {}
    for l in [x for x in o.split('\n') if x.strip()]:
        p = l.split()
        if len(p) >= 3:
            d[p[0]] = (p[1], p[2])
    a = d.get('/usr/share/nginx/html2')
    b = d.get('/probe/volume-on-missing-path')
    c = d.get('/usr/share/nginx/html')
    ok = a is not None and a == b and c is not None and a[0] != c[0]
    return ok, o.replace('\n', ' | ')


def c06_ro_bind_rejects_write():
    o = r(['docker', 'exec', 'kbst-web', 'sh', '-c',
           'echo x >> /etc/nginx/conf.d/default.conf 2>&1 | tail -1'])[1]
    return 'Read-only file system' in o, o


def c07_route_only_from_bind():
    o = r(['docker', 'exec', 'kbst-web', 'sh', '-c',
           'wget -q -O - http://127.0.0.1/storage-probe/ 2>&1 | head -1'])[1]
    return PROBE_TEXT in o, o[:120]


def c08_bind_shadows_image():
    """容器里的首页必须是 bind 那份，而不是镜像自带的 Welcome to nginx。"""
    inside = r(['docker', 'exec', 'kbst-web', 'sh', '-c', 'head -1 /usr/share/nginx/html/index.html'])[1]
    host = open(os.path.join(HERE, 'web-content', 'index.html'), encoding='utf-8', errors='replace').read().strip()
    ok = ('Welcome to nginx' not in inside) and (inside[:20] == host[:20])
    return ok, f'容器内={inside[:60]!r} 宿主={host[:60]!r}'


def c09_volume_prefilled():
    o = r(['docker', 'exec', 'kbst-web', 'sh', '-c', 'ls -l /var/log/nginx | head -4'])[1]
    ok = ('access.log' in o and '/dev/stdout' in o and 'error.log' in o and '/dev/stderr' in o)
    return ok, o.replace('\n', ' | ')[:200]


def c10_tmpfs_capacity(target='kbst-web', mountpoint='/cache'):
    o = r(['docker', 'exec', target, 'sh', '-c', f'df -k {mountpoint} 2>&1 | tail -1'])[1]
    parts = o.split()
    ok = len(parts) >= 3 and parts[1] == '32768'
    return ok, o


def c11_cross_system_size():
    inside = r(['docker', 'exec', 'kbst-web', 'sh', '-c', 'stat -c %s /usr/share/nginx/html/big.txt'])[1].strip()
    host = str(os.path.getsize(os.path.join(HERE, 'web-content', 'big.txt')))
    ok = inside == host == str(BIG_SIZE)
    return ok, f'容器内={inside} 宿主={host} 期望={BIG_SIZE}'


def c12_writable_layer_has_no_data():
    """可写层里只该有运行期垃圾：kbst-db 的 docker diff 不该出现 datadir 下的条目。"""
    o = r(['docker', 'diff', 'kbst-db'])[1]
    entries = [l for l in o.split('\n') if l.strip()]
    bad = [l for l in entries if '/var/lib/mysql' in l]
    return (not bad) and bool(entries), f'{len(entries)} 条，其中落在 datadir 的 {len(bad)} 条 {bad[:2]}'


CHECKS = [
    ('01 案例在跑且 db 健康', c01_running),
    ('02 数据基线 5000 行与聚合对得上', c02_data_baseline),
    ('03 挂载形态 3 bind + 4 volume', c03_mount_shape),
    ('04 /proc/mounts 里 9p/ext4/tmpfs 同框', c04_fstype),
    ('05 同一卷挂两处 = 同 dev 同 inode', c05_same_volume_two_paths),
    ('06 只读 bind 拒写并给出原文', c06_ro_bind_rejects_write),
    ('07 只存在于挂进来的那份配置里的路由', c07_route_only_from_bind),
    ('08 bind 遮蔽镜像出厂页', c08_bind_shadows_image),
    ('09 空命名卷被预填充（日志目录两条符号链接）', c09_volume_prefilled),
    ('10 tmpfs 容量按 size= 生效', c10_tmpfs_capacity),
    ('11 跨系统字节数两侧一致', c11_cross_system_size),
    ('12 可写层里没有数据文件', c12_writable_layer_has_no_data),
]


def run_all():
    fails = 0
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f'{type(e).__name__}: {str(e)[:120]}'
        print(f'  [{"PASS" if ok else "FAIL"}] {name} :: {detail}')
        fails += 0 if ok else 1
    print(f'checks={len(CHECKS)} FAIL={fails}')
    return 0 if fails == 0 else 1


def selftest():
    """三条坏样本必须被同一条判据抓到；抓不到就说明判据是假的。"""
    caught = 0
    ok1, d1 = c02_data_baseline(expect='4242\t1')
    print(f'  坏样本1（把期望聚合改成不可能值）{"被抓到" if not ok1 else "没抓到 → 判据失效"} :: {d1[:60]}')
    caught += 0 if ok1 else 1

    r(['docker', 'rm', '-f', 'kbst-verify-self'], tmo=90)
    r(['docker', 'run', '-d', '--name', 'kbst-verify-self', 'alpine:3.20', 'sleep', '60'], tmo=180)
    ok2, d2 = c10_tmpfs_capacity(target='kbst-verify-self', mountpoint='/cache')
    print(f'  坏样本2（没有 tmpfs 的容器）{"被抓到" if not ok2 else "没抓到 → 判据失效"} :: {d2[:70]}')
    caught += 0 if ok2 else 1
    r(['docker', 'rm', '-f', 'kbst-verify-self'], tmo=90)

    ok3, d3 = c03_mount_shape(over={'bind': 99, 'volume': 99})
    print(f'  坏样本3（期望 99 条 bind）{"被抓到" if not ok3 else "没抓到 → 判据失效"} :: {d3[:70]}')
    caught += 0 if ok3 else 1

    print(f'SELFTEST={"PASS" if caught == 3 else "FAIL"} 抓到 {caught}/3 条坏样本')
    return 0 if caught == 3 else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    print('先跑判据自证（证明这些判据会红），再跑主判据：')
    if selftest() != 0:
        print('判据自没过 → 主跑的 PASS 不可信，终止')
        sys.exit(2)
    sys.exit(run_all())
