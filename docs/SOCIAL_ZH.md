# 社交媒体发布素材

以下为待发布文案，未代发。配图使用本项目实际生成的三张角色海报；图中人物为非官方同人设定。
仓库：https://github.com/EdwinjJ1/moss-image-mac

## X：短帖

I got MOSS-Image running locally on my M1 Max Mac (32GB) via PyTorch/MPS. Open-sourced setup, a Gradio UI, and a chat-to-local-generation Skill. Real outputs + prompts + seeds included. Try it and share your Mac specs!

https://github.com/EdwinjJ1/moss-image-mac

配图：DeepSeek、Claude、ChatGPT 三张海报。建议正文使用这条短帖；安装细节可在后续回复补充仓库指南链接。

## 小红书

标题：用 Mac 画出三位 AI 少女

这三张 DeepSeek、Claude、ChatGPT 的拟人海报，都是在我的 MacBook 上用 MOSS-Image 生成的，英文标题也是模型直接画出来的，没有后期补字。

我基于 OpenMOSS 的开源模型做了 Apple Silicon 适配：用 PyTorch / Diffusers 接上 Metal/MPS，再通过分阶段加载和提示词缓存控制内存占用，支持 FP16 推理。

实测机器是 M1 Max、32GB 内存。这组三张是 768×1024、28 步，每张约 6 分钟。模型权重单独下载，生图推理在本机完成。

项目已经开源：安装步骤、网页怎么操作、怎么在支持本地执行的 AI 助手里通过对话出图，都写进了文档，样图的提示词、seed 和参数也公开了。

GitHub 搜索：EdwinjJ1/moss-image-mac

欢迎有 M 系列 Mac 的朋友试跑，告诉我你的芯片、内存和生成耗时。觉得有用的话，也欢迎点个 Star。

#Mac本地部署 #开源项目 #AI绘画 #MOSSImage #AppleSilicon

图片顺序：三张角色海报 → 本机网页操作截图（自行录制时注意私人信息）→ 仓库入门文档。

## 抖音

封面文字：这三张图，Mac 本地跑的

视频标题：把 MOSS-Image 搬上 MacBook，开源了

口播稿：

这三张 AI 少女海报，都是我在 MacBook 上用 MOSS-Image 跑出来的，连英文标题也是模型画的。

我做了苹果芯片适配，通过分阶段加载，让文本编码器和生成模型轮流使用 GPU，再加上提示词缓存和 FP16 推理。

机器是 M1 Max、32GB 内存，这组图每张大约六分钟。现在项目已经开源，安装、网页操作，还有在本地助手里对话出图的方法都写清楚了。

想试的话，去 GitHub 搜索 moss-image-mac。也欢迎把你的 Mac 实测结果发到仓库。

视频简介：

MOSS-Image for Mac 已开源。真实样图、提示词、seed、安装和对话出图指南都在仓库。
实测 M1 Max / 32GB；其他机型欢迎反馈。
GitHub：EdwinjJ1/moss-image-mac
#开源 #Mac #AI绘画 #本地部署 #MOSSImage

镜头建议：

1. 0–5 秒：快速展示三张完整海报。
2. 5–15 秒：切到 Mac 的本地生成页面，展示实际参数。
3. 15–25 秒：展示对话需求与助手调用本地脚本的过程。
4. 25–35 秒：展示仓库安装指南和样图参数，结束在仓库名称。

生成过程较长，可剪辑或加速录屏，并标明实际耗时，避免让观看者误以为实时秒出。
