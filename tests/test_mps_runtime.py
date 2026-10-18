"""Regression checks for Mac adaptation; no weights or GPU required."""
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import torch

import mps_runtime as runtime


class TimestepTests(unittest.TestCase):
    def test_cpu_patch_preserves_upstream_float64_math(self):
        source = (
            "import torch\nclass MOSSImagePipeline:\n"
            "    def embedding(self, times, half):\n"
            + runtime._FLOAT64_TIMESTEP + "        return embedding\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pipeline_moss_image.py").write_text(source)
            module = runtime._import_pipeline_module(root)
            times = torch.tensor([0.0, 0.125, 999.0], dtype=torch.float32)
            actual = module.MOSSImagePipeline().embedding(times, 128)
        phase = times.double()[:, None] * (10000 ** (-torch.arange(128, dtype=torch.float64) / 128))
        expected = torch.cat((phase.cos(), phase.sin()), -1).float()
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)

    def test_changed_upstream_source_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pipeline_moss_image.py").write_text("# incompatible upstream pipeline\n")
            with self.assertRaisesRegex(ValueError, "changed; update"):
                runtime._import_pipeline_module(root)


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        events = self.events

        class BasePipeline:
            def encode_prompt(self, prompt, max_sequence_length):
                if self.text_encoder is None:
                    raise AssertionError("Encoding requires the text encoder")
                events.append("encode")
                return torch.zeros(1, 2, 4), torch.ones(1, 2)

            def __call__(self, prompt, **kwargs):
                if self.transformer is None or self.text_encoder is not None:
                    raise AssertionError("Sampling must retain only the DiT")
                events.append("sample")
                return kwargs

        self.loader = Mock()
        module = SimpleNamespace(MOSSImagePipeline=BasePipeline, MOSSImageTransformer=self.loader)
        self.pipe = runtime._staged_pipeline_class(module)()
        self.pipe.root = Path("unused-model")
        self.pipe.text_encoder = None
        self.pipe.transformer = object()
        self.pipe.embeddings = OrderedDict()

        def load_text(*args, **kwargs):
            self.assertIsNone(self.pipe.transformer)
            self.events.append("load-text")
            return Mock()

        def load_dit(*args, **kwargs):
            self.assertIsNone(self.pipe.text_encoder)
            self.events.append("load-dit")
            return Mock()

        self.loader.from_pretrained.side_effect = load_dit
        self.text_patch = patch.object(runtime.AutoModel, "from_pretrained", side_effect=load_text)
        self.cache_patch = patch.object(runtime, "empty_cache")
        self.text_patch.start()
        self.cache_patch.start()
        self.addCleanup(self.text_patch.stop)
        self.addCleanup(self.cache_patch.stop)

    def test_both_prompts_encoded_before_sampling_and_cached(self):
        first = self.pipe("coffee", negative_prompt="blur")
        self.assertEqual(self.events, ["load-text", "encode", "encode", "load-dit", "sample"])
        self.events.clear()
        second = self.pipe("coffee", negative_prompt="blur", num_inference_steps=10, width=512)
        self.assertEqual(self.events, ["sample"])
        self.assertIs(first["prompt_embeds"], second["prompt_embeds"])

    def test_prompt_cache_evicts_least_recently_used(self):
        for index in range(runtime.CACHED_PROMPTS):
            self.pipe.encode_prompt(f"prompt-{index}")
        self.pipe.encode_prompt("prompt-0")
        self.pipe.encode_prompt("new")
        self.assertEqual(len(self.pipe.embeddings), runtime.CACHED_PROMPTS)
        self.assertIn((("prompt-0",), 4096), self.pipe.embeddings)
        self.assertNotIn((("prompt-1",), 4096), self.pipe.embeddings)


class IntegrationTests(unittest.TestCase):
    def test_mac_routing_and_unsupported_compile(self):
        import gradio_app

        with patch.object(runtime, "is_available", return_value=True), patch.object(runtime, "load_pipeline") as load:
            gradio_app.load_pipeline("model", "model", local_files_only=True)
            load.assert_called_once_with("model", local_files_only=True)
            with self.assertRaisesRegex(ValueError, "Compile DiT"):
                gradio_app.load_pipeline("model", "model", compile_transformer=True)

    def test_gradio_ui_builds_for_mac_without_loading_weights(self):
        import gradio_app

        with patch.object(runtime, "is_available", return_value=True), patch.object(runtime, "load_pipeline") as load:
            app = gradio_app.build_app("missing-model-directory")
            self.assertEqual(app.title, "MOSS-Image for Mac")
            load.assert_not_called()
            app.close()


if __name__ == "__main__":
    unittest.main()
