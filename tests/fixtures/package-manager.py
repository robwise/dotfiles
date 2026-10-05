"""Controlled external brew/ni/mise/Corepack boundary for managed Chezmoi tests."""
import json
import os
from pathlib import Path
import shlex
import sys
import tomllib

home = Path(os.environ['HOME'])
base = home.parent
bin_dir = home / 'Library/pnpm/bin'
command = sys.argv[1]
args = sys.argv[2:]
with (base / 'commands.jsonl').open('a') as log:
    log.write(json.dumps([command, *args]) + '\n')

def install(name, body):
    path = bin_dir / name
    path.write_text('#!/bin/sh\n' + body + '\n')
    path.chmod(0o755)

def wrapper(name):
    install(name, 'exec ' + ' '.join(shlex.quote(x) for x in [sys.executable, __file__, name]) + ' "$@"')

if command == 'brew':
    assert args == ['bundle', 'install', '--file=' + str(home / '.Brewfile'), '--no-upgrade']
    brewfile = (home / '.Brewfile').read_text()
    assert all('brew "' + prerequisite + '"' in brewfile for prerequisite in ['mise', 'ni', 'python'])
    wrapper('mise'); wrapper('ni')
    if not os.environ.get('FIXTURE_NO_PYTHON'):
        install('python3', 'exec ' + shlex.quote(sys.executable) + ' "$@"')
elif command == 'mise':
    configured = tomllib.loads((home / '.config/mise/config.toml').read_text())['tools']
    if args[0] == 'which':
        tool = args[1]
        assert tool in configured and args[2:] == ['--tool=' + tool]
        if not (base / ('installed-' + tool)).exists(): sys.exit(1)
        print(bin_dir / tool)
    elif args[0] == 'install':
        tool = args[1]
        assert tool in configured
        (base / ('installed-' + tool)).touch()
        if tool == 'node':
            wrapper('node'); install('corepack', '# Fixture Corepack launcher')
            install('yarn', '# Corepack conflict launcher')
    elif args[:2] == ['exec', '--']:
        executable = bin_dir / args[2]
        if not executable.exists():
            sys.stderr.write('Fixture missing prerequisite: ' + args[2] + '\n'); sys.exit(23)
        os.execv(str(executable), [str(executable), *args[3:]])
    else: raise AssertionError(args)
elif command == 'node':
    assert args == [str(bin_dir / 'corepack'), 'disable', 'yarn', '--install-directory', str(bin_dir)]
    assert (bin_dir / 'yarn').exists()
    (bin_dir / 'yarn').unlink()
elif command == 'ni':
    config = dict(line.split('=', 1) for line in (home / '.nirc').read_text().splitlines() if '=' in line)
    assert config['globalAgent'] == 'pnpm', 'Global manager must be derived from managed .nirc'
    assert args == ['-g', 'skills@latest', '@openai/codex@0.160.0'], 'Pinned managed Codex package required'
    assert not (bin_dir / 'yarn').exists(), 'Corepack conflict must be removed before global installation'
    assert all((base / ('installed-' + tool)).exists() for tool in ['node', 'pnpm', 'bun', 'yarn'])
    with (base / 'commands.jsonl').open('a') as log:
        log.write(json.dumps(['global-manager', config['globalAgent']]) + '\n')
    install('codex', 'exec /usr/bin/sandbox-exec -f ' + shlex.quote(str(base / 'deny-network.sb')) + ' ' + shlex.quote(os.environ['FIXTURE_CODEX']) + ' "$@"')
else: raise AssertionError(command)
