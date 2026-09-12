---
title: 函数式编程
linkTitle: 函数式编程
description: Lambda 表达式、函数接口（Supplier/Consumer/Function/Predicate）、方法引用等 Java 8 函数式编程核心内容。
weight: 4
---

函数式编程是 Java 8 最重要的变革：把「动作本身」作为值传递。本章聚焦 Lambda 表达式、`java.util.function` 标准函数接口、方法引用以及它们在 Stream 中的实际应用。

学习路线图：

```
Lambda 语法 → 四大函数接口 → 方法引用 → 自定义接口 → 默认方法
怎么写        谁产谁吃谁变谁断   极致简写   设计自己的签名    接口演化
        ↓
Stream 创建 → 终端归约 → 收集器 → 数值流 → 并行流
流水线搭建    产出结果    分拣打包   避开装箱   多分拣中心
        ↓
设计模式重构 → 思想与陷阱
结构坍缩       从会用到用得对
```
