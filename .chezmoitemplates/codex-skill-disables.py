"""Apply only checked-in skill exclusions using Codex's comment-preserving writer."""
import json
import os
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    names = json.load(sys.stdin)
    if not isinstance(names, list) or any(not isinstance(name, str) or not name.startswith('robwise-skills:') for name in names):
        raise ValueError('Expected qualified robwise-skills selectors')
    if not names:
        return
    home = Path(sys.argv[1]).expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    binary = shutil.which('codex')
    if not binary:
        raise RuntimeError('Codex CLI missing; apply the managed package installation first')
    environment = dict(os.environ, CODEX_HOME=str(home))
    errors = tempfile.TemporaryFile()
    child = subprocess.Popen([binary, 'app-server', '--listen', 'stdio://'], cwd=home.parent,
                             env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=errors)
    reader = selectors.DefaultSelector()
    reader.register(child.stdout, selectors.EVENT_READ)
    buffer = b''
    sequence = 0

    def send(message):
        child.stdin.write((json.dumps(message) + '\n').encode())
        child.stdin.flush()

    def call(method, params):
        nonlocal sequence, buffer
        sequence += 1
        wanted = sequence
        deadline = time.monotonic() + 15
        send({'id': wanted, 'method': method, 'params': params})
        while time.monotonic() < deadline:
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                response = json.loads(line)
                if response.get('id') == wanted and ('result' in response or 'error' in response):
                    if 'error' in response:
                        raise RuntimeError(f'Codex {method}: {response["error"]}')
                    return response['result']
                if response.get('id') is not None and 'method' in response:
                    raise RuntimeError('Unexpected Codex server request during settings update')
            if child.poll() is not None:
                errors.seek(0)
                raise RuntimeError(f'Codex exited during {method}: {errors.read().decode()[:1000]}')
            for key, _ in reader.select(.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if data:
                    buffer += data
        raise TimeoutError(f'Codex timed out during {method}')

    try:
        call('initialize', {'clientInfo': {'name': 'chezmoi_skill_defaults', 'version': '1'}})
        send({'method': 'initialized', 'params': {}})
        for name in names:
            result = call('skills/config/write', {'name': name, 'enabled': False})
            if result.get('effectiveEnabled') is not False:
                raise RuntimeError(f'Codex did not disable {name}')
    finally:
        child.terminate()
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=2)
        reader.close()
        errors.close()


if __name__ == '__main__':
    main()
