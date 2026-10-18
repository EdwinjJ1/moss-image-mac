---
name: moss-image-local-generation
description: Generate images with this repository's local MOSS-Image Mac server from a conversation. Use when the user wants actual local model output, rather than prompt writing alone.
---

Use a local shell-capable assistant on the same Mac as the model. Locate the repository from the user's project context; if absent, ask for its path. This skill can be copied elsewhere, so do not infer the repository from the installed skill directory.

The repository needs `.venv`, a complete model bundle and a running `scripts/gradio-mac.sh` service. Read `docs/GETTING_STARTED_ZH.md` or `docs/GETTING_STARTED.md` for setup if necessary. Do not download tens of GB or start a second model process without considering the user's existing installation.

From the repository root, check the service:

```bash
.venv/bin/python scripts/generate-local.py --check
```

Turn the request into a concrete positive prompt, preserving intended wording and scene requirements. Save it as a UTF-8 text file under `outputs/prompts/` using file tools, not shell interpolation of user text. Chinese or English prompts work; English captions were used for the anime gallery. The separate `moss-image-prompt-enhancer` skill can help with detailed captions or layouts, but is not required.

Generate through the existing server:

```bash
.venv/bin/python scripts/generate-local.py --prompt-file outputs/prompts/request.txt --width 512 --height 512 --steps 10 --seed 42
```

Use requested dimensions and sampling settings when supplied; dimensions must be positive multiples of 16. For a first smoke run, 512×512 / 10 steps / one image reduces waiting; gallery portraits use 768×1024 / 28 steps. Generate distinct prompts sequentially. Keep the server running until completion, report real progress, and do not retry a pending job by submitting a duplicate.

The final stdout is JSON containing local image paths, the original `parameters_json` path when found, and server status. Stderr carries progress. If the server uses a custom output directory or port, pass `--server-output-dir` or `--url` accordingly. Inspect the actual output image before reporting success. Return the image and original metadata path. A missing metadata match is not a fabricated record: inspect the server output directory.

Later requests normally generate a new image from a revised prompt. This is text-to-image generation, not image-conditioned editing or persistent visual conversation memory. Use the user's requested local model; do not substitute a remote image generator. Publishing outputs is a separate action and requires the user's request.
