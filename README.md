# ST Platform

空间转录组分析平台的统一底座，旨在将分散的空间转录组算法组织成可注册、可调用、可比较、可复现的系统。

## 核心目标

- 统一数据对象入口，兼容 `AnnData` / `SpatialData` 等主流格式
- 抽象任务类型，分离"任务"与"算法"的概念
- 提供算法注册表，支持内置算法和插件化扩展
- 提供本地执行器，实现最小执行闭环
- 预留 API / Web / 容器化扩展接口

## 目录结构

```text
st_platform/
├─ docs/
│  ├─ architecture.md
│  └─ project_roadmap.md
├─ examples/
│  └─ quickstart.py
├─ src/
│  └─ st_platform/
│     ├─ algorithms/
│     ├─ core/
│     ├─ data/
│     ├─ tasks/
│     ├─ workflows/
│     ├─ __init__.py
│     ├─ __main__.py
│     └─ cli.py
├─ tests/
├─ pyproject.toml
└─ README.md
```

## 功能特性

- 列出默认任务目录
- 列出已注册算法
- 使用 demo 数据执行最小闭环，验证 `task -> algorithm -> runner -> result` 完整链路

## 快速开始

在项目根目录执行：

```bash
export PYTHONPATH="./src"
python -m st_platform list-tasks
python -m st_platform list-algorithms
python -m st_platform run-demo --task domain_detection --algorithm mock-domain
python -m st_platform run-demo --task domain_detection --algorithm spagcn
python -m st_platform run-demo --task domain_detection --algorithm spagcn-lite
python -m unittest discover -s tests
```

## 真实空间域算法环境

`spagcn`、`graphst`、`sedr`、`ccst`、`const`、`deepst` 使用仓库中的真实算法代码，需要额外依赖；`spagcn-lite` 是无重型依赖的 fallback。

```bash
uv venv .venv-spagcn
UV_CACHE_DIR=/tmp/uv-cache uv pip install --python .venv-spagcn/bin/python -e . -e ../SpaGCN/SpaGCN_package -e ../GraphST -e ../SEDR pot torch-geometric opencv-python scikit-image torchvision scikit-network python-louvain
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm spagcn
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm graphst
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm sedr
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm ccst
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm const
.venv-spagcn/bin/python -m st_platform run-demo --task domain_detection --algorithm deepst
```

`const` 当前复用 conST 的模型编码器路径接入；原仓库训练入口依赖 `torch_sparse`，在本地 PyTorch/CUDA 组合不匹配时可先不安装。

## 开发路线

1. 接入 `Visium` 作为 MVP 数据入口
2. 选择 2-3 类核心任务，各接入 1 个代表性算法
3. 建立结果存储规范，接入最小 API / UI

详细规划见 [docs/project_roadmap.md](./docs/project_roadmap.md)。
