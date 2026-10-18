# Contributing

Thanks for helping make MOSS-Image usable on Mac. Chinese and English reports are welcome.

## Useful contributions

- Report your chip, unified memory, macOS and package versions with generation settings and elapsed time.
- Share a generated image with its `parameters.json`; say whether the prompt was already cached.
- Improve MPS compatibility, memory use, installation or documentation.

Open an issue before a large change. Keep pull requests focused, preserve upstream attribution,
and explain what you tested. Never commit model weights, local paths, credentials or personal outputs
without reviewing them. The `assets/samples/mac-chalkboard` directory is the maintainer's Mac example;
other bundled examples come from upstream.

## Local checks

```bash
python -m pip install -e '.[ui,dev]' -c constraints-mac.txt
python -m unittest discover -s tests -v
python -m compileall -q mps_runtime.py gradio_app.py inference_runtime.py
bash -n scripts/setup-mac.sh scripts/gradio-mac.sh scripts/fetch-modelscope.sh
```

CPU tests check staging, cache eviction, precision patching and device routing without downloading
weights. They do not establish that generation works on a particular Mac. For runtime changes,
also report a real MPS generation and its parameters. Start with a small image and few steps,
then compare a normal generation with the same prompt and seed.

Code contributions use the existing Apache-2.0 license. Keep original notices and authorship.
