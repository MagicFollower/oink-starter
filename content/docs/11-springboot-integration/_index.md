---
title: 与 Spring Boot 的集成
linkTitle: 与 Spring Boot 的集成
description: Spring Boot 2.7.18 + JDK 8 + RocketMQ 4.9.8 下六种消息的真实用法案例与 starter 版本基线。
type: docs
icon: fa-solid fa-gears
weight: 11
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

本分类把 Apache RocketMQ 的六种消息落到 Spring Boot 工程里怎么写：用哪套依赖、参数默认值是什么、`RocketMQTemplate` 的哪个方法对应哪种消息，以及哪些写法在 Broker 4.9.8 上根本不成立。机制原理不在这里重复，正文一律链接到第 4、5 章的对应页面。

证据口径：全部分类不依赖任何本机运行的工程，技术断言的出处只有三类——`rocketmq-spring` 仓库 tag `rocketmq-spring-all-2.2.3` 的源码与官方示例、上游 `apache/rocketmq-site` 的 4.x 与 5.0 中文文档、`rocketmq-all-4.9.8-bin-release` 发行包内 jar 的类结构实物取证。代码块里的输出行统一标注为「预期输出」并注明推定依据。

## 知识板块

- **集成基线** — 三条集成路线的选型、starter 2.2.3 的依赖基线、`rocketmq.*` 全参数默认值、自动装配生效与失效的确切条件。
- **六种消息实战** — 普通、批量、延时、定时、顺序、事务六类消息在 Spring Boot 里的写法、限制与常见坑。
