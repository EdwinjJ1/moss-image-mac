# MOSS-Image for Mac

**让 MOSS-Image 在 Apple Silicon Mac 上通过 PyTorch Metal/MPS 本地生成图片。**

[English](README.md) · [快速开始](#快速开始) · [实现原理](#实现原理) · [反馈机型](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose)

这是 [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image) 的实验性 Mac 适配分支，
由 [Evanlin](https://github.com/EdwinjJ1) 维护。模型和原始推理代码来自 OpenMOSS；本项目新增
MPS 分阶段推理、提示词缓存、FP16 DiT 支持和 Mac 启动脚本，沿用上游 Gradio 网页界面。

## Mac 本地生成的动漫角色

| DeepSeek | Claude | ChatGPT |
| --- | --- | --- |
| [![DeepSeek anime character](assets/samples/deepseek-anime/01.png)](assets/samples/deepseek-anime/01.png) | [![Claude anime character](assets/samples/claude-anime/01.png)](assets/samples/claude-anime/01.png) | [![ChatGPT anime character](assets/samples/chatgpt-anime/01.png)](assets/samples/chatgpt-anime/01.png) |
| [Prompt](assets/samples/deepseek-anime/prompt.txt) · [Parameters](assets/samples/deepseek-anime/parameters.json) | [Prompt](assets/samples/claude-anime/prompt.txt) · [Parameters](assets/samples/claude-anime/parameters.json) | [Prompt](assets/samples/chatgpt-anime/prompt.txt) · [Parameters](assets/samples/chatgpt-anime/parameters.json) |

DeepSeek、Claude、ChatGPT 的非官方同人角色设定，根据参考图中的人物特征，使用英文提示词生成。
三张均在同一台 M1 Max / 32GB Mac 上使用 MOSS-Image-SFT 生成：**768×1024、28 步、DiT float16**。
参考图中的人物特征被转写为文字描述；模型只接收文字输入。图中的英文标题和标语也由模型生成，未后期加字或修图。
[查看 seed、实际耗时与复现方法](assets/samples/README.md)。

![M1 Max 32GB Mac 本地生成的中文黑板图](assets/samples/mac-chalkboard/01.png)

*真实 Mac 出图：MOSS-Image-SFT，1024×1024，20 步，seed 42，BF16。
记录中的完整生成调用耗时 320.362 秒，包含加载、模型切换和保存，不代表所有配置下的速度。
[完整提示词和参数](assets/samples/mac-chalkboard/parameters.json)。当前启动脚本默认使用 FP16，
上图则是 BF16 生成的。*

## 能做什么

- 用苹果 GPU 在本地运行文生图。
- 分阶段加载文本编码器和扩散 Transformer，降低同时驻留的内存压力。
- 缓存最近八组提示词编码；只改 seed、尺寸或步数时可复用。
- 网页调整参数、生成图片，并保存图片和 `parameters.json`。
- 从 ModelScope 断点续传下载模型，服务端提供 SHA-256 时校验文件。
- 完成依赖安装和模型下载后，可离线启动。

## 兼容性与资源

| 硬件 | 当前状态 |
| --- | --- |
| M1 Max，32GB 统一内存 | 有上述 SFT 成功出图记录 |
| 其他 M 系列芯片及内存容量 | 欢迎实测，目前未在本项目中确认 |
| Intel Mac | Mac 启动脚本不支持 |
| NVIDIA CUDA | 保留上游执行路径，本次 Mac 版本未验证 |

建议先使用 **32GB 或更多统一内存**，为单个模型、下载文件和 Python 环境预留约 **40GB 磁盘空间**。
本地完整 SFT 模型约 25GB。32GB 是已测试配置，并非已证明的最低配置。
本版本尚未确认小内存 Mac 支持，也没有做权重量化。生成可能需要数分钟。

## 快速开始

使用原生 arm64 终端、PyTorch 支持的 macOS 版本，推荐 Python 3.12（项目最低要求 3.10）。
安装脚本默认使用 `python3`，也可通过 `MOSS_PYTHON=python3.12` 指定。

```bash
git clone https://github.com/EdwinjJ1/moss-image-mac.git
cd moss-image-mac
bash scripts/setup-mac.sh
bash scripts/fetch-modelscope.sh MOSS-Image-SFT
bash scripts/gradio-mac.sh
```

打开 **http://127.0.0.1:7860**。第一次建议选择 **512×512、10 步、1 张图**，确认能生成后再增加尺寸和步数。
新提示词需要先加载文本编码器，再切换到 DiT；相同提示词可复用编码缓存。加载阶段可能需要等待。

[constraints-mac.txt](constraints-mac.txt) 固定了本地使用过的五个主要运行库版本。
安装和下载需要网络；Mac 启动脚本只读取本地模型，关闭 Gradio 分析上报，默认仅监听本机地址。
图片和参数会保存到 `outputs/gradio/`。

### 改用 Hugging Face 下载

```bash
.venv/bin/hf download OpenMOSS-Team/MOSS-Image-SFT --local-dir models/MOSS-Image-SFT
bash scripts/gradio-mac.sh
```

也支持 Base：先运行 `bash scripts/fetch-modelscope.sh MOSS-Image-Base`，
然后启动时加 `--model "$PWD/models/MOSS-Image-Base"`。

### 比较推理精度

```bash
MOSS_MPS_DIT_DTYPE=bfloat16 bash scripts/gradio-mac.sh
```

启动脚本默认 DiT 使用 FP16，文本编码器使用 BF16，VAE 使用 FP32。
这是浮点推理精度设置，没有对模型权重做量化。

## 实现原理

Qwen 文本编码器约 17GB，扩散 Transformer 约 10GB，同时驻留会给 32GB Mac 带来内存压力。
[mps_runtime.py](mps_runtime.py) 先加载编码器计算提示词编码，释放编码器后再加载 DiT 采样。
这两个大模型只保留其中一个在 GPU 上，小型 VAE 保持驻留。

MPS 不支持上游时间步正弦编码中的 FP64 运算，因此把这一小段计算放到 CPU，保留原始 FP64 精度，
再将结果传回 MPS。适配通过定点替换上游 pipeline 源码完成；若源码发生变化，会明确报错。
此外，在清理缓存和同步前等待 Metal 复制完成，处理本地观察到的模型加载死锁。

FP16 DiT 使用苹果 GPU 的对应计算能力；八项 LRU 提示词缓存减少重复编码和模型切换。
这些改动用于推理适配，没有训练或修改模型权重。

## 常见问题

- **MPS 不可用：** 确认使用原生 arm64 Python 和兼容的 macOS/PyTorch。
  在终端执行 `.venv/bin/python -c 'import torch; print(torch.backends.mps.is_available())'` 检查。
- **模型不完整：** 重跑下载命令，可断点续传并校验。需要保留 `pipeline_moss_image.py` 和全部五个组件。
- **内存不足：** 关闭占用内存较大的应用，减小图片尺寸和生成数量。Mac 自动分阶段加载；
  CUDA 的 offload 模式和 Compile DiT 不适用于 MPS。
- **端口占用：** 启动时加 `--port 7861`。
- **时间步补丁不匹配：** 附模型 revision 和报错提 issue，避免在上游源码变化后静默改变计算。

## 参与与路线

欢迎[提交问题或机型实测](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose)，请附芯片、内存、
macOS、依赖版本、模型、精度、尺寸、步数、提示词是否已缓存，以及耗时。最好同时提供图片和参数文件。

近期先补机型兼容性表，进行 FP16/BF16 及冷提示词/缓存提示词的同条件性能对照，改善安装和内存问题排查。
量化及更低内存支持属于探索方向。开发与检查方法见 [CONTRIBUTING.md](CONTRIBUTING.md)。
[群分享文案与初期路线](docs/LAUNCH_ZH.md) 可直接取用。

## 上游与许可

代码沿用 [Apache-2.0](LICENSE)，保留上游作者署名与提交历史。
模型权重单独下载，使用条款请查看对应上游模型卡；仓库不包含模型权重。

- [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image)
- [原始中文说明](README_UPSTREAM_ZH.md) · [Original README](README_UPSTREAM.md)
- [中文用户指南](USERGUIDE_ZH.md) · [English user guide](USERGUIDE.md)
- [上游 ComfyUI 集成](comfyui/README_ZH.md)（Mac 推荐先走本页快速开始）

除明确标注的 Mac 样图外，仓库中的 showcase 图片与 website 继承自上游，不代表 Mac 实测。
本分支的发布流程不包含上游官网部署或 ComfyUI 注册发布。
