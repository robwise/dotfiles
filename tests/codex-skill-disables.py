"""Run the managed after-apply script against disposable homes, without network/auth."""
import json
import os
from pathlib import Path
import shutil
import shlex
import sys
import subprocess
import tempfile
import tomllib

SOURCE = Path(__file__).resolve().parents[1]
CODEX = shutil.which('codex')
CHEZMOI = shutil.which('chezmoi')
assert CODEX and CHEZMOI, 'Install managed Codex and chezmoi prerequisites first'

with tempfile.TemporaryDirectory(prefix='codex-disables-') as temporary:
    root = Path(temporary)
    source = root / 'source'
    source.mkdir()
    (source / '.chezmoidata').mkdir()
    (source / '.chezmoitemplates').mkdir()
    shutil.copyfile(SOURCE / '.chezmoitemplates/codex-skill-disables.py', source / '.chezmoitemplates/codex-skill-disables.py')
    for managed in ['run_onchange_after_30-install-packages.sh.tmpl', 'dot_Brewfile', 'dot_nirc', 'private_dot_config/mise/config.toml', '.chezmoidata/packages.toml']:
        destination = source / managed
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / managed, destination)
    shutil.copyfile(SOURCE / 'run_after_40-codex-skill-disables.sh.tmpl', source / 'run_after_40-codex-skill-disables.sh.tmpl')
    data = source / '.chezmoidata/codex-skill-disables.json'
    def selectors(names):
        data.write_text(json.dumps({'codexDisabledSkills': names}))
    selectors(['robwise-skills:exclusive'])
    profile = root / 'deny-network.sb'
    profile.write_text('(version 1)\n(allow default)\n(deny network*)\n')
    initial = '''# Preserve global comment.
model = "fixture-model"
approval_policy = "never"
cli_auth_credentials_store = "file"
[features]
plugins = false
remote_plugin = false
[[skills.config]]
# Preserve third-party comment.
name = "third-party:skill"
enabled = true
'''
    def machine(name):
        base = root / name
        home = base / 'home'
        (home / '.codex').mkdir(parents=True)
        config = home / '.codex/config.toml'
        config.write_text(initial)
        # A fresh machine starts without any managed global Codex executable.
        bin_dir = home / 'Library/pnpm/bin'
        bin_dir.mkdir(parents=True)
        brew = bin_dir / 'brew'
        provider = SOURCE / 'tests/fixtures/package-manager.py'
        brew.write_text('#!/bin/sh\nexec ' + ' '.join(shlex.quote(x) for x in [sys.executable, str(provider), 'brew']) + ' "$@"\n')
        brew.chmod(0o755)
        shutil.copyfile(profile, base / 'deny-network.sb')
        assert not (bin_dir / 'codex').exists()
        (base / 'chezmoi.toml').write_text('')
        return base, home, config
    machines = [machine('a'), machine('b')]
    def apply(machine, missing_python=False):
        base, home, config = machine
        environment = {key: value for key, value in os.environ.items() if key in ('PATH', 'LANG', 'LC_ALL', 'TMPDIR')}
        environment['HOME'] = str(home)
        environment['FIXTURE_CODEX'] = CODEX
        if missing_python: environment['FIXTURE_NO_PYTHON'] = '1'
        command = [CHEZMOI, '--source', str(source), '--destination', str(home), '--config', str(base / 'chezmoi.toml'), '--cache', str(base / 'cache'), '--persistent-state', str(base / 'state.boltdb'), '--refresh-externals=never', '--no-tty', 'apply']
        result = subprocess.run(command, env=environment, cwd=root, capture_output=True, timeout=30)
        if missing_python:
            assert result.returncode != 0 and 'missing prerequisite: python3' in result.stderr.decode(), result.stderr.decode()
            assert config.read_text() == initial
            return
        assert result.returncode == 0, result.stderr.decode()
        assert not (home / '.codex/auth.json').exists()
    def verify(machine, disabled):
        raw = machine[2].read_text()
        parsed = tomllib.loads(raw)
        assert '# Preserve global comment.' in raw and '# Preserve third-party comment.' in raw
        entries = parsed['skills']['config']
        assert next(entry for entry in entries if entry['name'] == 'third-party:skill')['enabled'] is True
        for name in disabled:
            assert next(entry for entry in entries if entry['name'] == name)['enabled'] is False
        parsed['skills']['config'] = [entry for entry in entries if not entry['name'].startswith('robwise-skills:')]
        assert parsed == tomllib.loads(initial)
    for fixture in machines:
        apply(fixture)
        verify(fixture, ['robwise-skills:exclusive'])
    # Inspect the actual managed installation process rather than pre-installing Codex.
    for base, home, config in machines:
        commands = [json.loads(line) for line in (base / 'commands.jsonl').read_text().splitlines()]
        assert ['ni', '-g', 'skills@latest', '@openai/codex@0.160.0'] in commands
        assert ['global-manager', 'pnpm'] in commands
        assert all(['mise', 'install', tool] in commands for tool in ['node', 'pnpm', 'bun', 'yarn'])
        assert any(command[0] == 'node' and command[2:4] == ['disable', 'yarn'] for command in commands)
        assert not (home / 'Library/pnpm/bin/yarn').exists()
        assert (home / 'Library/pnpm/bin/codex').exists()
    apply(machine('missing-python'), missing_python=True)
    # Unchanged source reasserts a manually changed setting; a second apply is byte-idempotent.
    config = machines[0][2]
    config.write_text(config.read_text().replace('name = "robwise-skills:exclusive"\nenabled = false', 'name = "robwise-skills:exclusive"\nenabled = true'))
    assert next(entry for entry in tomllib.loads(config.read_text())['skills']['config'] if entry['name'] == 'robwise-skills:exclusive')['enabled'] is True
    apply(machines[0]); verify(machines[0], ['robwise-skills:exclusive'])
    previous = config.read_bytes()
    apply(machines[0]); assert config.read_bytes() == previous
    selectors(['robwise-skills:second'])
    for fixture in machines:
        apply(fixture)
        verify(fixture, ['robwise-skills:exclusive', 'robwise-skills:second'])
    # Removed selectors remain locally disabled, but are no longer enforced.
    config.write_text(config.read_text().replace('name = "robwise-skills:exclusive"\nenabled = false', 'name = "robwise-skills:exclusive"\nenabled = true'))
    apply(machines[0])
    assert next(entry for entry in tomllib.loads(config.read_text())['skills']['config'] if entry['name'] == 'robwise-skills:exclusive')['enabled'] is True
    selectors([])
    previous = config.read_bytes()
    apply(machines[0]); assert config.read_bytes() == previous
    print('PASS: managed provisioning from missing Codex, pinned ni global routing, Mise installs, Corepack conflict removal, missing Python failure, initial defaults, both homes, unchanged-source reapply, byte-idempotence, selector replacement/removal, unrelated values/comments, no credentials or network')
