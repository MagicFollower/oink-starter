# 存储双案例：Nginx + MySQL（可直接跑，用来验 10-存储专题 的每一条说法）

这是 10-存储专题的**操作台**，不是阅读材料。正文里每一条「在某处写、在另一处看、重启之后还剩什么」的读数，都能在这个目录里用同两条命令复现。

## 一分钟起停

```bash
cd Docker知识库/示例/存储双案例
docker compose up -d --wait      # 起 db（MySQL 8.4）与 web（nginx 1.27-alpine），等到健康
docker exec -e MYSQL_PWD='KbSt#Test2026' kbst-db mysql -uroot -N -e "SELECT COUNT(*), SUM(CRC32(CONCAT(id,body,tag,crc))) FROM kbdb.t_note;"
start http://127.0.0.1:18899/     # Windows 侧打开站点内容
python verify_storage.py           # 逐条判据自己跑一遍（会打印 PASS/FAIL，且有 --selftest 会故意失败）
docker compose down                # 停并删容器，**保留卷**（数据还在）
docker compose down -v             # 连卷一起删，回到出厂空数据
```

出厂基线（本机实测，`down -v` 之后重新 `up` 会得到同一组数）：

- `kbdb.t_note` **5000 行**，聚合 `SUM(CRC32(...)) = 10728165079651`
- 站点首页是 bind 里那份 `web-content/index.html`（121 字节），**不是**镜像自带的 `/usr/share/nginx/html/index.html`
- `http://127.0.0.1:18899/storage-probe/` 回 `probe-ok from ro-bind config`（这条路由只存在于挂进去的那份配置里）

## 这个案例一次覆盖了五种存储形式

`compose.yaml`（1519 字节）里七条挂载 + 一条 tmpfs，逐条对应正文的一节：

| 挂什么 | 挂到哪 | 它在这套案例里证明什么 | 正文落点 |
|---|---|---|---|
| `mysqldata`（命名卷） | `/var/lib/mysql` | 数据库真数据的唯一正确落点；容器删了它还在 | 10.2 取舍、10.4 生命周期、10.6 冷备 |
| `./mysql-init`（只读 bind） | `/docker-entrypoint-initdb.d` | 初始化 SQL 只在数据目录为空时跑一次 | 10.5 应用时机、10.6「只备数据不备配置的代价」 |
| `./web-content`（可写 bind） | `/usr/share/nginx/html` | 宿主改一下容器立刻看见；同时把镜像原有内容**遮掉** | 10.3 穿层、10.5 覆盖规则、10.9 故障⑤ |
| `./nginx/default.conf`（只读 bind 单文件） | `/etc/nginx/conf.d/default.conf` | 配置进容器的第二条路；`:ro` 下写入失败是设计不是坏了 | 10.5 四条路、10.9 故障⑧ |
| `weblogs`（命名卷） | `/var/log/nginx` | **空卷挂到有内容的目录会预填充**：卷里出现 `access.log -> /dev/stdout` | 10.5 胜负规则、10.9 故障⑥ |
| `img2`（命名卷，挂两处） | `/usr/share/nginx/html2` 与 `/probe/volume-on-missing-path` | 一个卷两个挂载点是同一个对象（inode 相同）；挂到镜像没有的路径时不预填充 | 10.3 `stat` 那一格 |
| `tmpfs: /cache` | `/cache`（`size=32m,mode=1777`） | 只活着这一次；restart 之后内容清零；容量算进内存 | 10.4 生命周期、10.8 故障③ |

## 目录里都有什么

```text
compose.yaml              双案例定义（上面那张表的全部挂载）
nginx/default.conf        728 字节，含 /storage-probe/、/write-probe、/logs 三条路由
mysql-init/10-seed.sql     真数据：5000 行 + crc 校验列（顶部那行 SET SESSION 是有故事的，见下）
web-content/index.html     121 字节，用来对照镜像出厂页
web-content/big.txt        1179648 字节，用来做跨系统与穿层对账
verify_storage.py          判据脚本：逐条给 PASS/FAIL，--selftest 会故意让它红
backups/                 探针跑备份时用的目录（内容是可删的产物，不是案例资产）
```

两个容易踩的点：

1. **`10-seed.sql` 顶部那行 `SET SESSION cte_max_recursion_depth = 10000;` 不是装饰**。去掉它，5000 行的递归 CTE 会在第 1001 次迭代被中止，报 `ERROR 3636 (HY000) ... Recursive query aborted after 1001 iterations`；入口脚本因此半途退出，而容器**照样 healthy**、表里 **0 行**。这一格是 10.4 与 10.8 的实测素材，本机留了原始日志。
2. **不要手动改 `web-content/` 和 `nginx/default.conf`**。探针脚本会往里追加一行、再改回去；如果你在跑脚本的同时手改，收尾核对会被打乱。

## 清理与「不该动的东西」

- `docker compose down -v` 只删这个项目里的三个卷；匿名卷要用 `docker volume ls` 找到 id **按名删**。
- 判据脚本与被判据脚本都要跑：`python verify_storage.py --selftest` 应当报出它自己造的那条坏样本，否则 PASS 是空判。
- 这套案例与本机 Harbor 栈（9 个容器）共用一个引擎。**不要跑 `docker system prune`、不要动 daemon 配置**；卷名一律以 `kbst` 开头，删除时按名而不是按模式。
