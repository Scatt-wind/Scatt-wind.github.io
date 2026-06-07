---
title: Python 开发环境配置
date: 2026-06-01
excerpt: 使用 Anaconda 创建虚拟环境，隔离项目依赖，保持开发环境整洁。
tags: [Python, Anaconda]
---

在 Python 开发中，不同项目往往依赖不同版本的库。如果所有包装进同一个全局环境，版本冲突几乎是迟早的事。虚拟环境是解决这个问题最简单、也最被广泛接受的方式。

## 为什么需要虚拟环境

想象你同时维护一个使用 Flask 2.x 的博客和一个使用旧版依赖的自动化脚本。全局安装会让升级一个项目的依赖时，悄悄破坏另一个项目的运行环境。

> 隔离不是麻烦，而是对过去那个「能跑就别动」的自己的温柔保护。

### 常见方案对比

- **venv** — Python 内置，轻量无额外依赖
- **Conda** — 适合数据科学，可管理非 Python 依赖
- **Poetry** — 现代化的依赖与打包管理

## 使用 Conda 创建环境

```
conda create -n myproject python=3.11
conda activate myproject
pip install -r requirements.txt
```

激活环境后，终端提示符前会出现环境名称。此时安装的包只作用于当前环境，不会影响系统 Python。

## 保持环境整洁的习惯

每个项目根目录维护一份 `requirements.txt` 或 `pyproject.toml`，记录精确依赖。换机器或协作时，一条安装命令即可复现环境。

```
pip freeze > requirements.txt
pip install -r requirements.txt
```

环境配置看似琐碎，却是长期可维护开发的基石。花十分钟建好环境，能省下无数小时的排错时间。
