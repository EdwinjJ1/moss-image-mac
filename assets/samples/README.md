# Mac-generated sample gallery

All samples in this directory were generated locally with MOSS-Image-SFT on the maintainer's
M1 Max / 32 GB Mac. Other showcase assets elsewhere in the repository are inherited from upstream.

## English anime character posters

| DeepSeek | Claude | ChatGPT |
| --- | --- | --- |
| [![DeepSeek anime character](deepseek-anime/01.png)](deepseek-anime/01.png) | [![Claude anime character](claude-anime/01.png)](claude-anime/01.png) | [![ChatGPT anime character](chatgpt-anime/01.png)](chatgpt-anime/01.png) |
| [Prompt](deepseek-anime/prompt.txt) · [Parameters](deepseek-anime/parameters.json) | [Prompt](claude-anime/prompt.txt) · [Parameters](claude-anime/parameters.json) | [Prompt](chatgpt-anime/prompt.txt) · [Parameters](chatgpt-anime/parameters.json) |

These are unofficial fan interpretations of DeepSeek, Claude and ChatGPT, not official brand mascots.
User-provided reference screenshots informed the written character descriptions. They were not used
as image-conditioning inputs and are not redistributed here. This is text-to-image inference.
The PNG files are the model outputs, without post-generation lettering or retouching.

| Character | Seed | DiT precision | Recorded generation call |
| --- | --- | --- | --- |
| DeepSeek | 20261018 | float16 | 395.150 s |
| Claude | 20261019 | float16 | 367.596 s |
| ChatGPT | 20261020 | float16 | 344.072 s |

Shared settings: 768×1024, 28 steps, Euler, CFG 3, shift 5, negative branch skips layer 22,
one image per call. The prompts were new to this generation session and were processed sequentially.
Times are the app's full recorded generation calls, including any loading/staging and image saving;
they are not isolated denoising benchmarks or controlled speed comparisons with the BF16 example.

Each character directory includes:

- `01.png`: original locally generated image.
- `parameters.json`: original app-exported generation record, including prompt, seed, configuration hashes and software versions.
- `prompt-draft.json`: editable English caption.
- `prompt.txt`: compiled prompt, matching the recorded positive prompt.

## Reproduce

1. Follow the root README to install and download MOSS-Image-SFT.
2. Start with `bash scripts/gradio-mac.sh` for FP16 DiT; use the precision recorded above for each sample.
3. Paste a sample's `prompt.txt` into Prompt and its recorded `negative_prompt` into Negative prompt.
4. Set width 768, height 1024, steps 28, CFG 3, shift 5, the recorded seed, and negative-branch skip layer 22.
5. Generate one image. The output and its new metadata will be saved under `outputs/gradio/`.

Use `MOSS_MPS_DIT_DTYPE=bfloat16 bash scripts/gradio-mac.sh` to reproduce a BF16 sample.
Exact output may vary with hardware, model revision and dependencies. The configuration hashes
identify configuration files, not model weight contents.

To edit and compile a caption:

```bash
.venv/bin/python skills/moss-image-prompt-enhancer/scripts/compile_prompt.py \
  assets/samples/deepseek-anime/prompt-draft.json \
  --output assets/samples/deepseek-anime/prompt.txt
```

## Chinese chalkboard example

[Image](mac-chalkboard/01.png) · [Parameters](mac-chalkboard/parameters.json).
1024×1024, 20 steps, seed 42, BF16, recorded call 320.362 s. This earlier example uses a
different prompt, resolution and precision from the character gallery.
