# 从零安装、部署和操作

[English](GETTING_STARTED.md) · [首页](../README_ZH.md) · [对话生成图片](CHAT_ZH.md)

## 1. 先确认电脑与资源

目前有真实出图记录的是 **M1 Max / 32GB 统一内存**。其他 M 系列欢迎实测；Intel Mac 不适用。
32GB 是实测配置，不代表已验证的最低门槛。单个模型约 25GB，建议为模型、环境和下载临时文件预留约 40GB 磁盘。
首次安装和下载需要网络；模型与依赖完整后，生图推理可以本地离线运行。

准备原生 arm64 终端、Git、Python 3.12。Python 可从 [Python 官方 macOS 安装页](https://www.python.org/downloads/macos/) 获取。
如果已经安装 Homebrew，可运行 `brew install git python@3.12`。
首次运行 Git 若提示缺少 Apple Command Line Tools，按系统提示安装，或运行 `xcode-select --install`。
终端中检查：

```bash
uname -m
python3.12 --version
git --version
```

第一项应为 `arm64`，而不是 Rosetta 下的 `x86_64`。

## 2. 下载项目并安装依赖

```bash
git clone https://github.com/EdwinjJ1/moss-image-mac.git
cd moss-image-mac
MOSS_PYTHON=python3.12 bash scripts/setup-mac.sh
```

后续命令均在这个项目目录中运行。脚本会创建 `.venv`、安装 UI 和推理依赖，并检查 MPS。
不会在这一步下载模型。主要依赖版本见 [constraints-mac.txt](../constraints-mac.txt)。
已经有合适的 `python3` 时也可直接执行 `bash scripts/setup-mac.sh`。

成功时会看到 `MPS available`。也可手动检查：

```bash
.venv/bin/python -c 'import torch; print(torch.backends.mps.is_available())'
```

## 3. 下载一个模型

推荐先用 SFT，任选一个下载来源即可。

ModelScope（支持断点续传，服务端提供 SHA-256 时校验）：

```bash
bash scripts/fetch-modelscope.sh MOSS-Image-SFT
```

Hugging Face：

```bash
.venv/bin/hf download OpenMOSS-Team/MOSS-Image-SFT --local-dir models/MOSS-Image-SFT
```

下载到 `models/MOSS-Image-SFT/`，不要只下载 Transformer 权重。完整目录包含：

```text
models/MOSS-Image-SFT/
  pipeline_moss_image.py
  model_index.json
  text_encoder/
  transformer/
  tokenizer/
  scheduler/
  vae/
```

安装依赖、下载模型完成后，无需每次重复做。

## 4. 启动本地网页

```bash
bash scripts/gradio-mac.sh
```

保持这个终端窗口运行，用浏览器打开 **http://127.0.0.1:7860**。
这是自己电脑的地址，GitHub 仓库页面本身不提供在线生图服务。

首次建议 **512×512、10 步、1 张图**。生成时需等待模型加载、提示词编码、采样、解码和保存。
实际高清样图可能需要数分钟，不能保证秒出。Mac 自动使用分阶段 MPS 加载。

## 5. 在页面里怎么操作

1. **模型选择**：选择本地 `MOSS-Image-SFT`。不要误选需要联网下载的模型 ID。
2. **Prompt**：写出想画的主体、画风、构图、颜色和图中文字。中英文都可输入；仓库角色样图使用英文描述。
3. **Negative prompt**：填写希望避免的内容，可保留默认值。
4. **尺寸与 Steps**：先用小尺寸试跑，宽高须为 16 的正整数倍。
5. **Seed**：固定整数便于比较改动；`-1` 表示随机。
6. 点击 **Generate**，等待结果。高级参数先保留默认值：CFG 3、shift 5、负向分支跳层 22。
7. 在结果区域查看或下载图片；完整原图与参数会同时保存到磁盘。

先试这条简单提示词：

```text
A small blue whale floating above a girl's open palm, elegant anime illustration, underwater observatory, soft blue light, a clean heading reading "DIVE INTO IDEAS".
```

想复现角色海报：打开[样图画廊](../assets/samples/README.md)，将某张的 `prompt.txt` 和 `parameters.json` 中的负面提示词填入页面，
设置 768×1024、28 步及对应 seed。硬件、依赖和权重版本不同可能影响输出。

## 6. 图片和参数在哪

默认输出目录：

```text
outputs/gradio/<run-id>/
  01.png
  parameters.json
```

`parameters.json` 记录实际 prompt、seed、尺寸、步数、精度、依赖版本与生成调用耗时等。
对话调用脚本也会返回图片路径与匹配到的原始参数路径；客户端下载副本位于 `outputs/client/`。
这些输出默认不会提交到 Git。分享前可检查参数中的提示词是否包含私人内容。

## 7. 再次启动、停止与更新

再次使用只需进入项目目录，运行 `bash scripts/gradio-mac.sh`。停止服务：回到终端按 `Ctrl+C`。

端口冲突：

```bash
bash scripts/gradio-mac.sh --port 7861
```

打开 `http://127.0.0.1:7861`；对话脚本也要加 `--url http://127.0.0.1:7861`。
自定义输出目录可加 `--output-dir "$PWD/outputs/my-runs"`，对话脚本相应加 `--server-output-dir "$PWD/outputs/my-runs"`。

更新前停止服务，保留自己的修改：

```bash
git pull --ff-only
.venv/bin/python -m pip install -e '.[ui]' -c constraints-mac.txt
bash scripts/gradio-mac.sh
```

若 `git pull` 提示本地修改或分支冲突，先检查 `git status`，不要直接重置自己的文件。

## 8. 常见故障

| 现象 | 处理 |
| --- | --- |
| 找不到 Python / Git | 完成第 1 步，确认命令在终端可运行 |
| MPS 为 False | 检查 arm64 Python、终端架构与 macOS/PyTorch 兼容性 |
| 模型不完整 | 重跑下载命令，保留上面列出的全部组件 |
| 生成慢 | 新提示词需要加载编码器；同提示词只改 seed/尺寸/步数可复用编码缓存 |
| 内存不足 | 关闭高占用程序、减少尺寸和张数；不同时启动多个模型服务 |
| Pipeline changed | 上游 pipeline 与兼容补丁不匹配，附模型 revision 提 issue |
| 无法连接本地服务 | 保持启动终端运行，核对地址与端口 |

没有解决时，使用[故障反馈模板](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose)，附芯片、内存、系统、依赖版本、执行命令和报错。

## 9. 部署范围

这份指南部署在你自己的 Mac 上，默认仅监听 `127.0.0.1`，不带公网用户鉴权或云 GPU 托管。
要从同一台电脑的助手对话调用，继续看[对话生成指南](CHAT_ZH.md)。
