"""Set up the same project on Windows, Linux, and GitHub Codespaces."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
F5_COMMIT = '9c614e9657089213efc6a7421b30630be138a3f5'


def run(*command, **kwargs):
    subprocess.run([str(arg) for arg in command], cwd=ROOT, check=True, **kwargs)


def prepare_source():
    source = ROOT / 'F5-TTS'
    if not (source / 'pyproject.toml').exists():
        run('git', 'submodule', 'update', '--init', 'F5-TTS')
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != F5_COMMIT:
        raise SystemExit(f'Expected F5-TTS commit {F5_COMMIT}, found {actual}. Keep the pinned submodule version.')
    patch = ROOT / 'patches' / 'f5-windows-audio.patch'
    check = subprocess.run(['git', '-C', str(source), 'apply', '--check', str(patch)], capture_output=True)
    if check.returncode == 0:
        run('git', '-C', source, 'apply', patch)
    else:
        applied = subprocess.run(['git', '-C', str(source), 'apply', '--reverse', '--check', str(patch)], capture_output=True)
        if applied.returncode:
            raise SystemExit('The audio patch cannot be applied. Preserve local changes and inspect F5-TTS before setup.')
    print('Pinned F5-TTS source and WAV compatibility patch are ready.', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true', help='Validate source and apply the compatibility patch only.')
    parser.add_argument('--skip-model-download', action='store_true')
    parser.add_argument('--cpu', action='store_true', help='Install CPU-only PyTorch for Codespaces.')
    args = parser.parse_args()
    prepare_source()
    if args.prepare_only:
        return
    environment = ROOT / '.venv'
    python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    if args.cpu:
        run(python, '-m', 'pip', 'install', 'torch', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu')
    run(python, '-m', 'pip', 'install', '-e', ROOT / 'F5-TTS', '-r', ROOT / 'requirements.txt', '-r', ROOT / 'demo' / 'requirements.txt')
    run(python, '-c', 'import flask, flask_cors, f5_tts, whisper, sounddevice, sklearn, soundfile; print("Project dependencies load successfully.")')
    if not args.skip_model_download:
        run(python, '-c', 'import whisper; whisper.load_model("base"); print("Whisper base model is ready.")')
    print('Setup complete. Start .venv Python with imv_api.py, then open http://localhost:5000.', flush=True)


if __name__ == '__main__':
    main()
