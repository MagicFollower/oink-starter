---
title: File tree comments
type: docs
---

```filetree {title="Storage directory comments"}
rocksdb-data/
  data/
    m/    # schema store: property keys, vertex/edge/index labels, counters
    g/    # graph store: vertices, edges, index tables, olap tables
    s/    # system store: tasks, server info, backend meta (driver version)
  wal/
    m/
    g/
    s/
```

```filetree {title="Unbroken comment" wrap=true}
storage/
  id.txt    # abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
```

```filetree {title="Compact comments" wrap=false}
compact/
  config.yml    # An explicitly compact description stays on one line even when the text is too long for its column.
```

```filetree {title="Wrapped comments" wrap=true}
wrapped/
  a-deliberately-long-runbook-filename-for-a-failover-drill.md    # Complete recovery procedure: verify the previous leader, inspect replication, and only then promote the standby.
  graph/    # Graph storage: vertices, edges, index tables, and OLAP analysis data all remain readable.
    metadata.yml    # Backend metadata and driver version for the current storage engine.
```
