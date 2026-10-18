# Assets

- `images/<name>/`: live Gradio examples, each with `parameters.json` and an image.
  The JSON `image` field names the image file, relative to that example directory.
  Edit `parameters.seed` to set the example seed; `null` means the original seed is
  unknown and selects random generation. Examples retain their recorded prompts, seeds and sampling settings.
  The UI polls every two seconds. Editing the selected example reloads its fields;
  adding/removing folders updates the gallery. Write complete JSON files atomically
  to avoid exposing incomplete edits. Runtime memory/compile settings stay unchanged.
- `samples/`: selected Mac-generated MOSS-Image outputs, each accompanied by its `parameters.json`.
  See the [Mac sample gallery](samples/README.md) for the English character posters, prompts and measured generation times.

The Gradio app saves each run to `outputs/gradio/<run-id>/`, including PNG images
and a JSON record of the prompt, negative prompt, actual seed, dimensions, sampling
parameters, memory mode, model name, configuration hashes and software versions.
After validating a result, copy its complete run folder into `samples/<sample-name>/`.
Only add real model outputs; do not use placeholder art as a model-quality example.

The model directory is supplied separately so sample metadata does not publish
local filesystem paths. Model configuration hashes do not fingerprint the weights:
keep the exact checkpoint/revision when curating a sample. Seeds alone cannot
ensure identical results across different hardware or library versions.
