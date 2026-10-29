# 隔离与资源

> 容器是一个被管住的进程，不是一台小机器。

---

LLMS 索引： [llms.txt](/llms.txt)

---

容器是一个被管住的进程，不是一台小机器。

本板块包含：容器的本质、Namespace 与 Cgroups；联合文件系统与 OverlayFS。

---

本节页面：

- [容器的本质、Namespace 与 Cgroups](/docs/05-%E5%8E%9F%E7%90%86%E6%B7%B1%E5%85%A5/%E9%9A%94%E7%A6%BB%E4%B8%8E%E8%B5%84%E6%BA%90/%E5%AE%B9%E5%99%A8%E6%9C%AC%E8%B4%A8namespace%E4%B8%8Ecgroups/): unshare/lsns 手搓迷你容器；七种隔离；CPU/内存/IO 限制原理与 OOM Killer，137 的机制根据。
- [联合文件系统与 OverlayFS](/docs/05-%E5%8E%9F%E7%90%86%E6%B7%B1%E5%85%A5/%E9%9A%94%E7%A6%BB%E4%B8%8E%E8%B5%84%E6%BA%90/%E8%81%94%E5%90%88%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E4%B8%8E%E9%95%9C%E5%83%8F%E5%88%86%E5%B1%82/): lowerdir/upperdir/merged 与写时复制；GraphDriver 实地观察；站④分层能省体积的机制解释。
