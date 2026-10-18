# MOSS-Image for Mac

**Run MOSS-Image locally on an Apple silicon Mac with PyTorch Metal/MPS.**

[简体中文](README_ZH.md) · [Quick start](#quick-start) · [How it works](#how-it-works) · [Report your Mac](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose)

An experimental Mac adaptation of [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image),
maintained by [Evanlin](https://github.com/EdwinjJ1). The model and original inference code are by
OpenMOSS. This fork adds staged MPS inference, prompt embedding caching, FP16 DiT support,
and Mac launch scripts while retaining the upstream Gradio UI.

## Start here

| Goal | Guide |
| --- | --- |
| Install, download, launch, operate, save and update | [Step-by-step guide](docs/GETTING_STARTED.md) |
| Generate through a conversation with a local assistant | [Conversation guide and Skill](docs/CHAT.md) |
| Reproduce real Mac outputs | [Sample gallery and parameters](assets/samples/README.md) |

**Where do I type?** Use the browser Prompt field at `http://127.0.0.1:7860`, or a local shell-capable
assistant opened in this repository. The conversation workflow calls the same local model through
`scripts/generate-local.py`; the web UI itself is not a chat client.

## Anime characters, made on a Mac

| DeepSeek | Claude | ChatGPT |
| --- | --- | --- |
| [![DeepSeek anime character](assets/samples/deepseek-anime/01.png)](assets/samples/deepseek-anime/01.png) | [![Claude anime character](assets/samples/claude-anime/01.png)](assets/samples/claude-anime/01.png) | [![ChatGPT anime character](assets/samples/chatgpt-anime/01.png)](assets/samples/chatgpt-anime/01.png) |
| [Prompt](assets/samples/deepseek-anime/prompt.txt) · [Parameters](assets/samples/deepseek-anime/parameters.json) | [Prompt](assets/samples/claude-anime/prompt.txt) · [Parameters](assets/samples/claude-anime/parameters.json) | [Prompt](assets/samples/chatgpt-anime/prompt.txt) · [Parameters](assets/samples/chatgpt-anime/parameters.json) |

Three unofficial fan character concepts inspired by DeepSeek, Claude and ChatGPT.
Generated locally with MOSS-Image-SFT on the same M1 Max / 32 GB Mac: **768×1024, 28 steps, float16 DiT**.
The reference ideas were described in English prompts; the model received text only.
The headings and taglines are model-generated, with no lettering or image retouching afterward.
[Seeds, timings and reproduction details](assets/samples/README.md).

![Generated locally on an M1 Max / 32 GB Mac](assets/samples/mac-chalkboard/01.png)

*Real Mac output: MOSS-Image-SFT, 1024×1024, 20 steps, seed 42, BF16, 320.362 seconds
for the recorded generation call (including loading/staging and saving). This is one sample,
not a general performance claim. [Full prompt and parameters](assets/samples/mac-chalkboard/parameters.json).
The Mac launcher now defaults to FP16; the image above was generated with BF16.*

## What you get

- Local text-to-image generation on Apple silicon using Metal/MPS.
- Staged text encoder and diffusion transformer loading to reduce concurrent memory use.
- A cache for the last eight prompt embeddings: changing seed, dimensions or steps can reuse them.
- A Gradio browser interface with image and generation-parameter export.
- ModelScope downloads with resume and SHA-256 verification when provided by the server.
- Offline launch after downloading the model and installing dependencies.

## Compatibility

| Hardware | Status |
| --- | --- |
| M1 Max, 32 GB unified memory | Recorded successful SFT generation shown above |
| Other M-series chips / memory sizes | Community testing welcome; not yet verified here |
| Intel Mac | Unsupported by the Mac launcher |
| NVIDIA CUDA | Upstream execution path retained; not validated by this Mac release |

Start with **32 GB or more unified memory** and about **40 GB free disk space** for one model,
its download files and the Python environment. The local complete SFT bundle occupies about 25 GB.
32 GB is the tested configuration, not a proven minimum. Lower-memory Macs and quantization
are not established by this release. Inference can take minutes.

## Quick start

Use a native arm64 terminal, a macOS version supported by your PyTorch build, and Python 3.12
(recommended; project minimum 3.10). The installer uses `python3` by default;
set `MOSS_PYTHON=python3.12` if needed.

```bash
git clone https://github.com/EdwinjJ1/moss-image-mac.git
cd moss-image-mac
bash scripts/setup-mac.sh
bash scripts/fetch-modelscope.sh MOSS-Image-SFT
bash scripts/gradio-mac.sh
```

Open **http://127.0.0.1:7860**. For a first run, set **512×512, 10 steps, one image**.
Use more steps and a larger size after verifying that generation works.
The first new prompt loads the text encoder, then the DiT; repeated prompts can skip encoding.
Do not interpret a period of model loading as a failed generation.

The installer constrains the five main runtime packages to the versions used locally in
[constraints-mac.txt](constraints-mac.txt). Downloads require an internet connection.
The Mac launcher uses only local model files, disables Gradio analytics and binds to localhost.
Generated images and `parameters.json` are saved under `outputs/gradio/`.

### Download from Hugging Face instead

```bash
.venv/bin/hf download OpenMOSS-Team/MOSS-Image-SFT --local-dir models/MOSS-Image-SFT
bash scripts/gradio-mac.sh
```

Base is also available. Download it with `bash scripts/fetch-modelscope.sh MOSS-Image-Base`,
then pass `--model "$PWD/models/MOSS-Image-Base"` to the Mac launcher.

### Compare precision

```bash
MOSS_MPS_DIT_DTYPE=bfloat16 bash scripts/gradio-mac.sh
```

Default DiT precision is FP16 in the launcher. The text encoder uses BF16 and the VAE FP32.
These are floating-point inference modes; no weight quantization is applied.

## How it works

The Qwen text encoder (~17 GB) and diffusion transformer (~10 GB) create memory pressure
when resident together on the tested 32 GB Mac. [mps_runtime.py](mps_runtime.py) loads the
text encoder to produce prompt embeddings, releases it, then loads the DiT for sampling.
Only one of those two large models is kept on the GPU at a time; the small VAE stays resident.

MPS does not support the upstream timestep sinusoid's FP64 calculation. That calculation
runs on CPU at FP64 precision and returns the result to MPS. A targeted pipeline patch fails
with an explicit error if the upstream source changes. The runtime also drains pending Metal
copies before cache clearing/synchronization to avoid a loading deadlock observed locally.

The default launcher uses FP16 DiT arithmetic. Prompt embeddings use an eight-entry LRU cache,
which saves encoding and model-swapping work for repeated prompts. This adapts inference;
it does not train or modify the model weights.

## Troubleshooting

- **MPS unavailable:** use native arm64 Python and a supported macOS/PyTorch combination.
  Run `.venv/bin/python -c 'import torch; print(torch.backends.mps.is_available())'` in Terminal.
- **Missing/incomplete model:** rerun the download command. It resumes partial files and verifies
  completed files. Keep the full bundle, including `pipeline_moss_image.py` and all five components.
- **Memory exhausted:** close other memory-heavy apps; reduce resolution and image count.
  Mac uses staged loading automatically. CUDA offload modes and Compile DiT are unavailable on MPS.
- **Port in use:** run `bash scripts/gradio-mac.sh --port 7861`.
- **Pipeline changed / precision patch mismatch:** preserve the error and open an issue with
  the model revision. The compatibility check intentionally stops instead of silently changing math.

## Contributing and roadmap

[Report bugs or hardware results](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose).
Please include chip, memory, macOS, dependency versions, model, precision, dimensions, steps,
cold/warm prompt status and elapsed time. Images with their `parameters.json` are especially useful.

Near-term work: expand the hardware compatibility table, publish controlled FP16/BF16 and
cold/warm prompt comparisons, and improve first-run installation and memory diagnostics.
Quantization and lower-memory support are exploratory. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Upstream and license

Code is under [Apache-2.0](LICENSE); upstream authorship and commit history are preserved.
Model weights are downloaded separately: consult the corresponding upstream model card for their
terms. No model weights are included in this repository.

- [OpenMOSS/MOSS-Image](https://github.com/OpenMOSS/MOSS-Image)
- [Original README](README_UPSTREAM.md) · [原始中文说明](README_UPSTREAM_ZH.md)
- [Original user guide](USERGUIDE.md) · [中文用户指南](USERGUIDE_ZH.md)
- [Upstream ComfyUI integration](comfyui/README.md) (not the recommended Mac quick start)

Except for the labeled Mac samples above, bundled showcase images and the website are inherited
from upstream and should not be read as Mac benchmarks. Upstream homepage deployment and
ComfyUI registry publishing are not part of this fork's release process.
