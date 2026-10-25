---
title: "集群与运维"
linkTitle: "集群与运维"
description: "把单机推进到三节点 ensemble，覆盖选主、管理面、监控、快照、日志与常见故障。"
type: docs
icon: fa-solid fa-server
weight: 3
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

把单机推进到三节点 ensemble，覆盖选主、管理面、监控、快照、日志与常见故障。

## 知识板块

- **集群与一致性** — 三节点配置、myid、投票端口、Leader 选举与 ZAB 写入路径。
- **管理面与监控** — AdminServer、四字命令与四条监控通道：管理接口怎么开、怎么关，监控数据从哪条路来。
