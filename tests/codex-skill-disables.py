"""Run the managed after-apply script against disposable homes, without network/auth."""
import json
import os
from pathlib import Path
import shutil
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
        # Stub only the prerequisite command wrapper; run the real Codex binary under network denial.
        bin_dir = home / 'Library/pnpm/bin'
        bin_dir.mkdir(parents=True)
        mise = bin_dir / 'mise'
        mise.write_text('#!/bin/sh\nshift 2\nexec "$@"\n')
        mise.chmod(0o755)
        codex = bin_dir / 'codex'
        codex.write_text(f'#!/bin/sh\nexec /usr/bin/sandbox-exec -f "{profile}" "{CODEX}" "$@"\n')
        codex.chmod(0o755)
        (base / 'chezmoi.toml').write_text('')
        return base, home, config
    machines = [machine('a'), machine('b')]
    def apply(machine):
        base, home, config = machine
        environment = {key: value for key, value in os.environ.items() if key in ('PATH', 'LANG', 'LC_ALL', 'TMPDIR')}
        environment['HOME'] = str(home)
        command = [CHEZMOI, '--source', str(source), '--destination', str(home), '--config', str(base / 'chezmoi.toml'), '--cache', str(base / 'cache'), '--persistent-state', str(base / 'state.boltdb'), '--refresh-externals=never', '--no-tty', 'apply']
        result = subprocess.run(command, env=environment, cwd=root, capture_output=True, timeout=30)
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
    print('PASS: initial defaults, both homes, unchanged-source reapply, byte-idempotence, selector replacement/removal, unrelated values/comments, no credentials or network')
