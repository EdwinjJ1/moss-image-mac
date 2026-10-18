# 在哪里通过对话生成图片

[English](CHAT.md) · [安装与网页操作](GETTING_STARTED_ZH.md)

## 三个入口

| 入口 | 在哪里输入 | 谁负责生成 |
| --- | --- | --- |
| 网页 | 本机浏览器 `http://127.0.0.1:7860` 的 Prompt 输入框 | Mac 上的 MOSS-Image |
| 对话 | 同一台 Mac 上，已打开项目且能执行本地命令的 AI 助手对话，例如 Codex 本地项目 | 助手整理提示词，脚本调用本机 MOSS-Image |
| 终端 | 项目目录中执行 `scripts/generate-local.py` | 同一个本机服务 |

当前 Gradio 网页是参数式生图界面，没有内置聊天窗口。对话入口依赖助手的本地命令能力，
不会因为你在普通聊天网页贴入一个 localhost 地址就自动连接到 Mac。

图像推理在本地运行；使用的对话助手可能需要联网、账号或订阅。助手的服务条款、数据处理与费用独立于本项目。

## 方法 A：无需安装 Skill，直接在项目对话里用

1. 按[安装指南](GETTING_STARTED_ZH.md)完成环境和模型下载。
2. 在终端运行 `bash scripts/gradio-mac.sh` 并保持运行。
3. 在支持本地执行命令的助手里打开这个项目目录，进入该项目的对话。
4. 发送这段话，并在后面写你的画面需求：

```text
请读取 skills/moss-image-local-generation/SKILL.md，
通过 scripts/generate-local.py 调用我本机的 MOSS-Image，实际生成一张图片。
请保存提示词，生成后给我图片和原始 parameters.json 的路径。
先用 512×512、10 步、seed 42。
画面：一位蓝发鲸鱼少女，在水下图书馆托着一只小鲸鱼，动漫风格。
```

助手应实际执行命令并返回图片，而不仅是回复一段 prompt。执行权限由助手环境控制，若提示本地权限不足，按该环境的机制处理。
修改需求可继续说：

```text
保留刚才的提示词结构，把背景换成星空，seed 保持不变，再生成一张。
```

这是修改提示词后重新生成；不是以原图为输入的局部编辑，也不是模型自动记住此前图片。

## 方法 B：可选安装到 Codex 的个人 Skill 目录

在项目根目录运行，目标不存在时才复制，避免覆盖已有个人 Skill：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R -n skills/moss-image-local-generation "$HOME/.agents/skills/"
```

在这个项目的对话里调用 `$moss-image-local-generation`；若未出现，可重新打开客户端或让助手直接读取仓库中的 Skill 文件。
个人目录中的 Skill 不绑定项目绝对路径，跨项目使用时要告诉助手仓库在哪。

Skill 路径与调用方式依据 [OpenAI 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)。不同助手的发现与安装方式可能不同；
方法 A 的“读取文件并执行脚本”不依赖自动发现。

原有的 `skills/moss-image-prompt-enhancer` 只扩写或编译提示词，单独使用它不会生成图片。
新增加的 `moss-image-local-generation` 才会指导助手实际调用本地服务。

## 方法 C：终端调用，也供其他助手集成

检查服务，不生成图片：

```bash
.venv/bin/python scripts/generate-local.py --check
```

直接传一条提示词：

```bash
.venv/bin/python scripts/generate-local.py \
  --prompt 'A tiny blue whale swimming through a sunlit library, anime illustration' \
  --width 512 --height 512 --steps 10 --seed 42
```

复用文件中的提示词：

```bash
.venv/bin/python scripts/generate-local.py \
  --prompt-file assets/samples/deepseek-anime/prompt.txt \
  --width 768 --height 1024 --steps 28 --seed 20261018
```

完整复现还需从对应 `parameters.json` 复制 `negative_prompt`，用 `--negative-prompt` 传入。
脚本默认 SFT、CFG 3、shift 5、负向分支跳层 22、单张图片。`--help` 查看全部选项。

标准错误输出进度；最后一行标准输出是 JSON：

```json
{"images":["/absolute/path/to/image.png"],"parameters_json":"/absolute/path/to/parameters.json","status":"Saved ..."}
```

路径由实际运行返回，不要照抄上面的示意路径。若参数文件为 `null`，核对 `--server-output-dir`，图片仍可能已经生成。
不要因为等待较久就重复提交同一任务。不同提示词建议依次生成。

## 常见连接问题

- 连接失败：先启动网页服务，核对端口。自定义端口用 `--url http://127.0.0.1:7861`。
- 自定义输出目录：加 `--server-output-dir`，与网页启动的 `--output-dir` 一致。
- 助手在远端机器：它的 localhost 不是你的 Mac。本指南要求同机本地执行，不提供公网接入。
- 用户要求编辑参考图片：目前本项目提供文生图，可将图片特征转述为提示词；不要宣称支持尚未实现的图生图编辑。
