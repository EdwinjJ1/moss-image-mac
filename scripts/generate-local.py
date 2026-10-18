#!/usr/bin/env python3
"""Call the running local Gradio server from a terminal or tool-enabled assistant."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--prompt')
    source.add_argument('--prompt-file', type=Path)
    parser.add_argument('--url', default='http://127.0.0.1:7860')
    parser.add_argument('--check', action='store_true', help='Check API availability without generating')
    parser.add_argument('--model', default=str(ROOT / 'models/MOSS-Image-SFT'))
    parser.add_argument('--width', type=int, default=512)
    parser.add_argument('--height', type=int, default=512)
    parser.add_argument('--steps', type=int, default=10)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--cfg', type=float, default=3.0)
    parser.add_argument('--shift', type=float, default=5.0)
    parser.add_argument('--negative-prompt', default='nsfw, low quality, blurry, bad anatomy, watermark')
    parser.add_argument('--server-output-dir', type=Path, default=ROOT / 'outputs/gradio')
    args = parser.parse_args(argv)
    parsed = urlparse(args.url)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
        parser.error('--url must address the local server (localhost / loopback)')
    if not args.check and not (args.prompt or args.prompt_file):
        parser.error('provide --prompt or --prompt-file, or use --check')
    return args


def find_metadata(directory, prompt, image):
    digest = hashlib.sha256(image.read_bytes()).digest()
    for path in sorted(directory.glob('*/parameters.json'), key=lambda p: p.stat().st_mtime_ns, reverse=True):
        record = json.loads(path.read_text())
        if record['parameters']['prompt'] != prompt:
            continue
        for name in record['images']:
            original = path.parent / name
            if original.is_file() and hashlib.sha256(original.read_bytes()).digest() == digest:
                return str(path.resolve())
    return None


def main(argv=None):
    args = parse_args(argv)
    from gradio_client import Client
    client = Client(args.url, verbose=False, analytics_enabled=False, download_files=str(ROOT / 'outputs/client'))
    api = client.view_api(print_info=False, return_format='dict')
    if '/generate' not in api.get('named_endpoints', {}):
        raise ValueError('This server does not expose /generate. Start scripts/gradio-mac.sh.')
    if args.check:
        print(json.dumps({'ready': True, 'url': args.url, 'endpoint': '/generate'}))
        return
    prompt = args.prompt_file.read_text(encoding='utf-8').strip() if args.prompt_file else args.prompt.strip()
    sys.path.insert(0, str(ROOT))
    from gradio_app import GenerationConfig
    config = GenerationConfig(prompt=prompt, negative_prompt=args.negative_prompt, width=args.width,
                              height=args.height, steps=args.steps, seed=args.seed, cfg=args.cfg, shift=args.shift)
    config.validate()
    job = client.submit(args.model, prompt, args.negative_prompt, args.height, args.width,
                        args.steps, args.cfg, args.shift, args.seed, 1, '22', '', 0.0, 0.0, 1.0,
                        'model', False, api_name='/generate')
    last = None
    while not job.done():
        status = job.status()
        message = ' | '.join(p.desc for p in status.progress_data or [] if p.desc) or str(status.code)
        if message != last:
            print(message, file=sys.stderr, flush=True)
            last = message
        time.sleep(2)
    gallery, status = job.result()
    paths = [Path(item['image']).resolve() for item in gallery]
    metadata = find_metadata(args.server_output_dir, prompt, paths[0]) if paths else None
    print(json.dumps({'images': [str(p) for p in paths], 'parameters_json': metadata, 'status': status}, ensure_ascii=False))
    if metadata is None:
        print('Original metadata not found in --server-output-dir; check the server output directory.', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Error: {error}\nStart the local UI with: bash scripts/gradio-mac.sh', file=sys.stderr)
        sys.exit(1)
