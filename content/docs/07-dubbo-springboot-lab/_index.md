---
title: "Dubbo 实战"
linkTitle: "Dubbo 实战"
description: "从空目录开始，用 Spring Boot 2.7.18、Java 8、Dubbo 3.2.20 与 ZooKeeper 搭一套可运行的多模块 RPC 工程：模块拆分、契约、配置、提供者、消费者、动态引用、验收与排障。"
type: docs
icon: fa-solid fa-flask
weight: 7
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

从空目录开始，用 Spring Boot 2.7.18、Java 8、Dubbo 3.2.20 与 ZooKeeper 搭一套可运行的多模块 RPC 工程：模块拆分、契约、配置、提供者、消费者、动态引用、验收与排障。

## 知识板块

- **工程蓝图** — 先明确实战目标、业务场景与模块边界，再把最终代码结构、构建顺序和依赖关系画成地图，避免一上来就堆代码。
- **契约与底座** — 先把接口、DTO、分组与路由表定下来，再准备 ZooKeeper 和 Spring Boot 配置，让后续编码有稳定边界。
- **服务实现** — 分别从提供者和消费者两侧落地代码：暴露服务、静态引用、运行期动态引用，以及超时、重试和缓存。
- **运行与交付** — 把工程真正跑起来：构建、启动顺序、端到端调用、ZooKeeper 核对、失败恢复、常见故障与上线检查。
