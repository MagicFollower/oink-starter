---
title: 文档
linkTitle: 文档
description: 【文档区一句话摘要，会显示在侧边栏下拉卡片上】
type: docs
icon: fa-solid fa-book
sidebar_root_for: self
sidebar_root_link_self: true
menus:
  main:
    identifier: docs
    weight: 20
cascade:
  type: docs
  footer_style: slim
---

【一到两句：这套文档按什么顺序读、以哪个版本为主干、其他版本怎么标注。】

- [【分类A名】](/docs/01-【目录A】/)
- [【分类B名】](/docs/02-【目录B】/)
- [【分类C名】](/docs/03-【目录C】/)
{.cards}

<!--
落地清单：
1. 链接条目数必须等于 content/docs 下一级分类目录数，顺序与 weight 一致；
2. 每行形如 `- [显示名](/docs/NN-目录名/)`，末尾 `{.cards}` 决定渲染成卡片而非列表，别删；
3. menus.main 让「文档」出现在顶栏，identifier 全站唯一。
-->
