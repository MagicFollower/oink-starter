---
title: "Dubbo 集成"
linkTitle: "Dubbo 集成"
description: "从 Dubbo 架构、选型与运行时拓扑，到注册发现流程、生效原理和 ZooKeeper 节点读写，再用可运行工程完成一次真实集成。"
type: docs
icon: fa-solid fa-plug
weight: 6
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

从 Dubbo 架构、选型与运行时拓扑，到注册发现流程、生效原理和 ZooKeeper 节点读写，再用可运行工程完成一次真实集成。

## 知识板块

- **架构与选型** — 先看清 Dubbo 的角色与调用链，再回答为什么把注册中心交给 ZooKeeper，以及两者合用后的运行时边界。
- **注册与发现** — 沿着一次服务上下线，看清谁写了哪些节点、谁在监听、通知如何变成可用地址列表，以及这套机制为什么能生效、何时会失灵。
- **集成实践** — 用一套 Spring Boot 2.7 + Dubbo 3.2.20 的可运行工程，把依赖、配置、提供者、消费者、动态引用和验收步骤串起来。
