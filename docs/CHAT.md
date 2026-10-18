# Where to generate images through conversation

[简体中文](CHAT_ZH.md) · [Installation and web operation](GETTING_STARTED.md)

| Entry point | Where to type | Execution |
| --- | --- | --- |
| Web UI | Prompt field at `http://127.0.0.1:7860` | Local MOSS-Image |
| Conversation | A shell-capable assistant opened in this project on the same Mac, such as a local Codex project | Assistant writes a prompt; the script calls local MOSS-Image |
| Terminal | `scripts/generate-local.py` from the repository | Same local service |

The Gradio UI has prompt/parameter controls, not a built-in chat window. A regular web chat cannot
reach your Mac merely because you paste a localhost URL. The assistant needs local command execution.
Image inference is local; your assistant may separately use network services, accounts or subscriptions.

## Use directly without installing a skill

1. Follow the installation guide and download SFT.
2. Start `bash scripts/gradio-mac.sh` and leave it running.
3. Open this project directory in a local shell-capable assistant.
4. Send:

```text
Read skills/moss-image-local-generation/SKILL.md. Use scripts/generate-local.py
with my local MOSS-Image to actually generate one image, save the prompt, and return
the image plus the original parameters.json path. Start with 512×512, 10 steps, seed 42.
Scene: a blue-haired whale-themed anime woman holding a tiny whale in an underwater library.
```

The assistant should execute generation, not stop after providing a prompt. Its host controls command
permissions. For a follow-up, ask it to revise the previous prompt, retain the seed and generate again.
This generates a new image from text; it does not provide image-conditioned editing or automatic visual memory.

## Optional Codex skill installation

From the repository root, copy only if the destination does not already exist:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R -n skills/moss-image-local-generation "$HOME/.agents/skills/"
```

Invoke `$moss-image-local-generation` in this project's conversation. If undiscovered, restart the client
or explicitly ask it to read the repository skill file. When using the installed skill outside this project,
provide the repository path. Discovery and invocation follow [official OpenAI Skills documentation](https://learn.chatgpt.com/docs/build-skills).
Other assistant hosts may differ; explicitly reading the file does not require skill discovery.

The existing `moss-image-prompt-enhancer` only prepares prompts. The new `moss-image-local-generation`
skill instructs the assistant to execute real local generation.

## CLI integration

```bash
.venv/bin/python scripts/generate-local.py --check
.venv/bin/python scripts/generate-local.py \
  --prompt 'A tiny blue whale swimming through a sunlit library, anime illustration' \
  --width 512 --height 512 --steps 10 --seed 42
```

Or use a UTF-8 file:

```bash
.venv/bin/python scripts/generate-local.py \
  --prompt-file assets/samples/deepseek-anime/prompt.txt \
  --width 768 --height 1024 --steps 28 --seed 20261018
```

For full gallery settings, also pass the recorded `negative_prompt` using `--negative-prompt`.
Defaults: SFT, CFG 3, shift 5, skip layer 22 in the negative branch, one image. See `--help`.
Progress goes to stderr. The final stdout line is JSON with `images`, `parameters_json` and `status`.
The image paths refer to actual downloaded local files. A null metadata path means no matching original
record was found; check `--server-output-dir`. Do not resubmit a still-pending task.

Use `--url http://127.0.0.1:7861` for a changed port and `--server-output-dir` if the server uses a custom output directory.
The script accepts only loopback addresses. Remote assistants' localhost addresses are not your Mac;
this guide does not expose your service publicly. Reference images can inform text descriptions, but
this workflow does not implement image-to-image editing.
