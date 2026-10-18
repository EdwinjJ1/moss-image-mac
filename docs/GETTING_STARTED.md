# Install, deploy and use

[简体中文](GETTING_STARTED_ZH.md) · [Home](../README.md) · [Generate through conversation](CHAT.md)

## Prerequisites

The recorded configuration is an M1 Max / 32 GB unified-memory Mac. Other M-series configurations
need testing; Intel Macs are unsupported by the launcher. Allow about 40 GB free disk for one model
(about 25 GB), the environment and download files. Internet is needed for setup; installed local
inference can run offline. Use a native arm64 terminal, Git and Python 3.12.

Get Python from [the official macOS downloads](https://www.python.org/downloads/macos/), or, if Homebrew
is already installed, run `brew install git python@3.12`. If Git requests Apple Command Line Tools,
follow the OS prompt or run `xcode-select --install`.

```bash
uname -m
python3.12 --version
git --version
```

The architecture should be `arm64`.

## Install the project

```bash
git clone https://github.com/EdwinjJ1/moss-image-mac.git
cd moss-image-mac
MOSS_PYTHON=python3.12 bash scripts/setup-mac.sh
```

Run the remaining commands from this directory. The installer creates `.venv`, installs dependencies
with `constraints-mac.txt`, and checks MPS. It does not download weights. An appropriate default
`python3` also works with `bash scripts/setup-mac.sh`. Confirm MPS manually if needed:

```bash
.venv/bin/python -c 'import torch; print(torch.backends.mps.is_available())'
```

## Download one model

Choose either source, not both:

```bash
bash scripts/fetch-modelscope.sh MOSS-Image-SFT
```

Or:

```bash
.venv/bin/hf download OpenMOSS-Team/MOSS-Image-SFT --local-dir models/MOSS-Image-SFT
```

Keep the entire bundle: `pipeline_moss_image.py`, `model_index.json`, `text_encoder/`, `transformer/`,
`tokenizer/`, `scheduler/`, and `vae/`. ModelScope downloads support resume and server-provided SHA-256 verification.

## Launch and operate

```bash
bash scripts/gradio-mac.sh
```

Keep the terminal running and open **http://127.0.0.1:7860** in your browser. This is your Mac;
the GitHub repository does not host an online generator.

1. Select the local SFT model directory.
2. Describe the subject, style, composition, colors and intended lettering in **Prompt**.
3. Keep or customize **Negative prompt**.
4. Start with **512×512, 10 steps, one image**. Dimensions must be positive multiples of 16.
5. Choose a fixed **Seed** for comparisons; `-1` selects a random seed.
6. Click **Generate**. Leave advanced settings at CFG 3, shift 5 and negative-branch skip layer 22 initially.
7. Wait for loading, encoding, sampling, decoding and saving. Larger outputs can take minutes.
8. View/download the result. Files are also saved on disk.

Try: `A tiny blue whale swimming through a sunlit library, elegant anime illustration`.
For the [character gallery](../assets/samples/README.md), copy its prompt and negative prompt,
set 768×1024, 28 steps and the recorded seed. Versions and hardware can affect exact output.

## Outputs and lifecycle

Original images and metadata are saved as:

```text
outputs/gradio/<run-id>/01.png
outputs/gradio/<run-id>/parameters.json
```

The metadata records the actual prompt, seed, dimensions, settings, precision, package versions
and generation-call timing. The conversation client also returns image and original metadata paths;
client downloads are under `outputs/client/`. Outputs are ignored by Git. Review prompts before sharing metadata.

Stop with `Ctrl+C` in the server terminal. Next time, enter the project directory and run the launcher again;
there is no need to reinstall or redownload. Change port with `--port 7861`, then open port 7861 in the browser.
Change output directory with `--output-dir "$PWD/outputs/my-runs"`. Pass the matching `--url` and
`--server-output-dir` to the conversation client.

To update, stop the server first:

```bash
git pull --ff-only
.venv/bin/python -m pip install -e '.[ui]' -c constraints-mac.txt
bash scripts/gradio-mac.sh
```

If Git reports local changes or diverged history, inspect `git status` and preserve your work.

## Troubleshooting and deployment scope

| Problem | Action |
| --- | --- |
| Python / Git missing | Complete prerequisite installation and verify commands |
| MPS unavailable | Check native arm64 Python and compatible macOS/PyTorch |
| Incomplete model | Resume downloading the entire bundle |
| Slow generation | New prompts require encoder loading; reused prompts can skip encoding |
| Memory exhausted | Reduce dimensions/count, close heavy apps, avoid multiple model servers |
| Pipeline changed | Report model revision and error; the compatibility patch needs updating |
| Cannot connect | Keep the server running and check its port |

This guide deploys on your own Mac, listening on localhost by default. It does not set up public hosting,
cloud GPU inference or user authentication. Use [issue templates](https://github.com/EdwinjJ1/moss-image-mac/issues/new/choose)
for unresolved problems, including hardware, versions, command and traceback. Continue with the
[conversation guide](CHAT.md) to control the same service from a local assistant.
