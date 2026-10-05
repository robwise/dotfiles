## Portability

This repository exists to reproduce the machine setup on a new computer.
Record every setup change and fix in managed chezmoi files or scripts, including
prerequisites and conflict handling. Setup work is complete only when the
repository's setup process reproduces the result on a supported new machine
without relying on commands run manually during the session. Validate that
process, not just the current machine's state.

## Agent skills

### Issue tracker

Issues and specs live in Linear. Before reading or publishing tickets,
read `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage roles. Before labeling tickets,
read `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context layout. Before exploring domain concepts
or architectural decisions, read `docs/agents/domain.md`.

### Global Node packages

Before installing or updating global Node packages,
read `docs/agents/global-node-packages.md`.

## README

Keep tool entries to the tool's purpose, our current approach, and an upstream
documentation link.
