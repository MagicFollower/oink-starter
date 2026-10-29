---
title: 文件树注释
type: docs
---

```filetree {title="存储目录注释"}
rocksdb-data/
  data/
    m/    # 元数据存储：属性键、顶点标签、边标签、索引标签和计数器
    g/    # 图数据存储：顶点、边、索引表，以及 OLAP 分析任务使用的数据表
    s/    # 系统存储：任务、服务器信息，以及包括驱动版本在内的后端元数据
  wal/
    m/
    g/
    s/
```

```filetree {title="无空格注释" wrap=true}
storage/
  id.txt    # abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
```

```filetree {title="紧凑注释" wrap=false}
compact/
  config.yml    # 显式关闭换行后，较长的配置说明仍然保持单行，并在当前注释列的边界处显示省略号。
```

```filetree {title="换行注释" wrap=true}
wrapped/
  a-deliberately-long-runbook-filename-for-a-failover-drill.md    # 完整恢复流程：先确认原主节点状态，再检查复制进度，最后才将备用节点提升为主节点。
  graph/    # 图存储：顶点、边、索引表，以及 OLAP 分析任务使用的数据表，全部保持完整可读。
    metadata.yml    # 当前存储引擎的后端元数据与驱动版本。
```
