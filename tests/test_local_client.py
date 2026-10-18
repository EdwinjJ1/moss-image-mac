"""Check original-metadata matching without a running model."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('local_client', Path(__file__).resolve().parents[1] / 'scripts/generate-local.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class MetadataTests(unittest.TestCase):
    def test_repeated_prompt_matches_image_bytes_instead_of_latest_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for name, content in [('earlier', b'original image'), ('later', b'different image')]:
                folder = root / name
                folder.mkdir()
                (folder / '01.png').write_bytes(content)
                metadata = folder / 'parameters.json'
                metadata.write_text(json.dumps({'parameters': {'prompt': 'same prompt'}, 'images': ['01.png']}))
                paths.append(metadata)
            downloaded = root / 'download.png'
            downloaded.write_bytes(b'original image')
            self.assertEqual(client.find_metadata(root, 'same prompt', downloaded), str(paths[0].resolve()))
            self.assertIsNone(client.find_metadata(root, 'unrelated prompt', downloaded))

    def test_local_check_needs_no_prompt_and_preserves_custom_port(self):
        args = client.parse_args(['--check', '--url', 'http://localhost:7861'])
        self.assertTrue(args.check)
        self.assertEqual(args.url, 'http://localhost:7861')


if __name__ == '__main__':
    unittest.main()
