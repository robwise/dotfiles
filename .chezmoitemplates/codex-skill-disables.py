"""Apply checked-in skill exclusions through Codex's comment-preserving writer."""
import json
import os
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


class CodexSettingsClient:
    def __init__(self, binary, home):
        self.errors = tempfile.TemporaryFile()
        self.child = subprocess.Popen(
            [binary, 'app-server', '--listen', 'stdio://'],
            cwd=home.parent,
            env=dict(os.environ, CODEX_HOME=str(home)),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.errors,
        )
        self.reader = selectors.DefaultSelector()
        self.reader.register(self.child.stdout, selectors.EVENT_READ)
        self.buffer = b''
        self.sequence = 0

    def initialize(self):
        self._call('initialize', {
            'clientInfo': {'name': 'chezmoi_skill_defaults', 'version': '1'},
        })
        self._send({'method': 'initialized', 'params': {}})

    def disable(self, name):
        result = self._call('skills/config/write', {'name': name, 'enabled': False})
        if result.get('effectiveEnabled') is not False:
            raise RuntimeError(f'Codex did not disable {name}')

    def close(self):
        self.child.terminate()
        try:
            self.child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.child.kill()
            self.child.wait(timeout=2)
        self.reader.close()
        self.errors.close()
        self.child.stdin.close()
        self.child.stdout.close()

    def _send(self, message):
        self.child.stdin.write((json.dumps(message) + '\n').encode())
        self.child.stdin.flush()

    def _call(self, method, params):
        self.sequence += 1
        wanted = self.sequence
        deadline = time.monotonic() + 15
        self._send({'id': wanted, 'method': method, 'params': params})
        while time.monotonic() < deadline:
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                response = json.loads(line)
                if response.get('id') == wanted and ('result' in response or 'error' in response):
                    if 'error' in response:
                        raise RuntimeError(f'Codex {method}: {response["error"]}')
                    return response['result']
                if response.get('id') is not None and 'method' in response:
                    raise RuntimeError('Unexpected Codex server request during settings update')
            if self.child.poll() is not None:
                self.errors.seek(0)
                raise RuntimeError(f'Codex exited during {method}: {self.errors.read().decode()[:1000]}')
            for key, _ in self.reader.select(.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if data:
                    self.buffer += data
        raise TimeoutError(f'Codex timed out during {method}')


def read_selectors():
    names = json.load(sys.stdin)
    if not isinstance(names, list) or any(
        not isinstance(name, str) or not name.startswith('robwise-skills:')
        for name in names
    ):
        raise ValueError('Expected qualified robwise-skills selectors')
    return names


def main():
    names = read_selectors()
    if not names:
        return
    binary = shutil.which('codex')
    if not binary:
        raise RuntimeError('Codex CLI missing; apply the managed package installation first')
    home = Path(sys.argv[1]).expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    client = CodexSettingsClient(binary, home)
    try:
        client.initialize()
        for name in names:
            client.disable(name)
    finally:
        client.close()


if __name__ == '__main__':
    main()
