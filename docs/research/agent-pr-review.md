# Agent PR review for robwise/dotfiles

Research note, 2026-10-08. All sources were accessed on 2026-10-08 unless
noted. Vendor products in this space change monthly; anything marked
**[version]** or **[plan]** depends on a version or plan and should be
rechecked before you rely on it.

Question: what is the cheapest, safest way to get an automatic agent review
on every PR to this public, solo-maintained chezmoi repo? The review should
catch **docs drift**, meaning `docs/inventory.md` and `docs/usage.md` no
longer match the setup, as `AGENTS.md` requires. General review would be a
bonus.

## TL;DR

- **Recommended start:** use the `anthropics/claude-code-action@v1` GitHub
  Action. Authenticate with `CLAUDE_CODE_OAUTH_TOKEN` from
  `claude setup-token`, which draws on your Pro/Max subscription, so there
  is no per-token bill. Trigger on `pull_request`, and give it a **custom,
  docs-drift-specific `prompt`** that posts inline comments. Actions minutes
  are free on public repos. *(My recommendation, details in
  [Recommendation](#6-recommendation).)*
- **Don't rely on the stock review plugin for docs drift.** The quick-setup
  review workflow runs the `code-review` plugin. Its source looks only for
  `CLAUDE.md` files, and this repo has only `AGENTS.md`. It also skips any PR
  that already has a Claude comment, so it won't re-review after you push a
  fix
  ([plugin source](https://github.com/anthropics/claude-code/blob/602df92bf481ed904533e95c09f740f40aab5aed/plugins/code-review/commands/code-review.md)).
- **Anthropic's managed "Code Review"** needs no workflow, but it is
  **Team/Enterprise only**. It averages **$15–25 per review**, and its docs
  name `CLAUDE.md` and `REVIEW.md` as its guidance files, not `AGENTS.md`
  ([Code Review](https://code.claude.com/docs/en/code-review)). It isn't an
  option on Pro or Max.
- **GitHub Copilot code review** reads `AGENTS.md` natively and needs no
  secret. It is **not included in Copilot Free**. On Pro ($10/mo, 1,500 AI
  credits = $15/mo, shared with all Copilot use), the default "Balanced"
  effort costs about $0.25–5 per review, so pick "Lite" ($0.05–1)
  ([Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review),
  [plans](https://docs.github.com/en/copilot/get-started/plans)).
  It is a good second opinion if you already pay for Copilot.
- **CodeRabbit** is free for public repos, but **public repos with fewer
  than 10 stars must trigger reviews manually**. This repo has 1 star, so
  it gets no automatic reviews for now
  ([CodeRabbit plans](https://docs.coderabbit.ai/management/plans.md)).
- **Security:** PRs here come from same-repo branches that you author, so
  `pull_request` with secrets is fine. Never use `pull_request_target` with
  a PR checkout. Guard the job to same-repo PRs. The Action, Copilot, and
  CodeRabbit are documented (or shown in source) to read some reviewer
  instructions from the **PR head**, so a PR can rewrite part of what its
  own reviewer is told. Under the Action's default App auth, a PR that
  edits the workflow file itself is skipped
  ([details](#4-security-for-a-public-repo)).
- **Repo gotcha:** a new root `CLAUDE.md` or `REVIEW.md` would be deployed
  to `~` by chezmoi unless you add it to `.chezmoiignore`. Dot-prefixed paths
  such as `.github/` and `.coderabbit.yaml` are ignored automatically
  ([chezmoi](https://www.chezmoi.io/reference/source-state-attributes/)).
  Adding a reviewer is a setup change, so under `AGENTS.md` it also needs
  `docs/inventory.md` and `docs/usage.md` updates.

---

## 1. Options and how each works

### 1a. `anthropics/claude-code-action` (GitHub Action)

State at access time: tag `v1` → latest release **v1.0.247 (2026-10-08)**.
The action installs **Claude Code 2.1.295**
(`base-action/action.yml`, `CLAUDE_CODE_VERSION="2.1.295"`, at commit
`2dca132`) **[version]**. Source:
[repo](https://github.com/anthropics/claude-code-action).

**Auth options**
([GitHub Actions docs](https://code.claude.com/docs/en/github-actions)):

| Input | What it is | Billing |
| - | - | - |
| `anthropic_api_key` | Claude Console API key | Per token, at [API prices](https://platform.claude.com/docs/en/about-claude/pricing) |
| `claude_code_oauth_token` | Token from `claude setup-token`; "available on Pro, Max, Team, and Enterprise plans" | "runs use your Claude subscription instead of API billing" |
| `anthropic_federation_rule_id` + `anthropic_organization_id` (+ optional service account and workspace IDs) | Workload identity federation: GitHub OIDC is exchanged for API access. No stored secret | API billing via a Console service account |
| `use_bedrock` / `use_vertex` / `use_foundry` | Cloud provider via OIDC, "so you store no static cloud credentials" | Your cloud bill |

- `claude setup-token` makes a **one-year** OAuth token. The token "can
  only make model requests" and "requires a Pro, Max, Team, or Enterprise
  plan" ([authentication](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token)).
  Set a calendar reminder to rotate it.
- The docs advise using an API key, not an OAuth token, for a secret shared
  across an org, "since an OAuth token is tied to the subscription of the
  person who ran `claude setup-token`". That doesn't matter for a solo repo.
- The GitHub side is separate. By default the action exchanges the job's
  OIDC token (`id-token: write`) for a **Claude GitHub App** token. If you
  pass `github_token`, it uses that token instead
  ([token.ts](https://github.com/anthropics/claude-code-action/blob/2dca132ff0e0c4094ce6048b422c6915a071210b/src/github/token.ts)).

**Setup paths.** `/install-github-app` in Claude Code installs the App,
stores the secret (`ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`), and
pushes a branch with `claude.yml` and, optionally, a review workflow. Manual
setup does the same three steps by hand. Both need repo admin
([docs](https://code.claude.com/docs/en/github-actions#setup)).

**Triggers and modes**
([docs](https://code.claude.com/docs/en/github-actions#interactive-and-automation-modes)):

- **Interactive mode** (no `prompt` input): responds to `@claude` in
  issue/PR comments and reviews.
- **Automation mode** (`prompt` set): runs on any event, such as
  `pull_request: [opened, synchronize, ready_for_review, reopened]`.
  "By default, results appear in the workflow run log rather than a comment."
  Claude posts only when the prompt tells it to and it has a posting tool.
- Before running, the action checks that the triggering actor has **write
  access** and that bots are not allowed, unless the bot is listed in
  `allowed_bots`.

**How the review prompt is configured.** You have two choices:

1. A plain-text `prompt` plus `claude_args` (for example `--allowedTools`,
   `--model`, `--max-turns`). Anthropic's example review workflow tells
   Claude to use `gh pr comment` for top-level feedback and
   `mcp__github_inline_comment__create_inline_comment` (with
   `confirmed: true`) for line comments
   ([solutions.md](https://github.com/anthropics/claude-code-action/blob/main/docs/solutions.md)).
2. A skill, either `/skill-name` from the repo's `.claude/skills/` (requires
   `actions/checkout`) or a plugin skill. The quick-setup review workflow
   uses `/code-review:code-review --comment …` from the `code-review` plugin
   ([docs](https://code.claude.com/docs/en/github-actions#run-a-skill)).

**Inline comments: yes.** The action starts its inline-comment MCP server
"only when `--allowedTools` in `claude_args` names it". With `--comment`,
the review is posted "as an inline comment on each issue it finds or as one
summary comment when it finds none"
([docs](https://code.claude.com/docs/en/github-actions#run-a-skill)).
Inline comments without `confirmed: true` are buffered and then classified
before posting (`classify_inline_comments`, default `true`)
([action.yml](https://github.com/anthropics/claude-code-action/blob/main/action.yml)).

**What the stock `code-review` plugin does**
([source at `602df92`](https://github.com/anthropics/claude-code/blob/602df92bf481ed904533e95c09f740f40aab5aed/plugins/code-review/commands/code-review.md)):

- **Step 1 skips** a PR that is closed, is a draft, "does not need code
  review (e.g. automated PR, trivial change…)", or where "Claude has already
  commented on this PR". *Consequence (my inference):* after the first
  review, pushing a fix gets no re-review.
- **Step 2 collects only `CLAUDE.md` files.** The compliance agents audit
  against those files, and the false-positive list excludes anything not
  "explicitly required in CLAUDE.md". *Consequence (my inference):* in this
  repo, which has `AGENTS.md` and no `CLAUDE.md`, the plugin is unlikely to
  enforce the docs-update rule. The Claude Code CLI itself does load
  `AGENTS.md` (see §2).

**Cost model.** Each run uses GitHub Actions minutes plus model tokens
([docs](https://code.claude.com/docs/en/github-actions#manage-costs)).
"GitHub Actions usage is free … for public repositories that use standard
GitHub-hosted runners"
([GitHub billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)).
Tokens are billed per token with an API key, or against your plan limits
with an OAuth token. Documented cost controls: `--max-turns`, `--model`, job
timeouts, and `concurrency`.

### 1b. Anthropic-managed options and built-in commands

| Feature | What it is | Who can use it | Cost |
| - | - | - | - |
| **Code Review** (managed) | Admin enables it at claude.ai; the Claude GitHub App runs a multi-agent review on Anthropic infra. Inline comments with severity labels, plus a neutral "Claude Code Review" check run. Triggers: once after PR creation, every push, or manual (`@claude review`, `@claude review always`). Fork PRs only on `@claude review` | "research preview, available for **Team and Enterprise** subscriptions" **[plan]** | "Each review averages $15-25", billed as usage credits outside plan usage |
| **`/code-review`** (built-in CLI command; `/review` is an alias since v2.1.223) | Local review of your branch, a PR number, or a ref range. `--comment` posts inline comments on a GitHub PR; `--fix` applies the findings. Follows `CLAUDE.md` like any session but does **not** read `REVIEW.md` | Any Claude Code user | Counts toward normal usage |
| **Ultrareview** (`/code-review ultra`, `claude ultrareview <PR> --post`) | Deeper cloud multi-agent review. `--post` adds one plain PR comment from your GitHub account. The `claude ultrareview` subcommand works in CI but needs a claude.ai login and usage credits | Pro/Max: "3 free runs" (one-time), then usage credits **[plan]** | "typically $5 to $25" per review |

Sources: [Code Review](https://code.claude.com/docs/en/code-review),
[ultrareview](https://code.claude.com/docs/en/ultrareview).

**How these differ from the Action.** Code Review is managed: no workflow,
no secret in the repo, and Anthropic tunes it from 👍/👎 reactions. It
needs a Team/Enterprise org. The Action runs on your runner with your
prompt and your credential. `/code-review` is local and on demand, not
automatic on each PR.

**Docs-drift relevance.** Code Review's docs say it reads `CLAUDE.md`
"bidirectionally: if your PR changes code in a way that makes a `CLAUDE.md`
statement outdated, Claude flags that the docs need updating too", and that
`REVIEW.md` rules "land more reliably than the same rules in a long
`CLAUDE.md`". That is the right shape for this repo, but the plan gate rules
it out.

### 1c. GitHub Copilot code review

- **Plans [plan]:** Copilot Free "does not include Copilot code review".
  Code review is included on Pro ($10/mo, 1,500 AI credits), Pro+ ($39/mo,
  7,000), and Max ($100/mo, 20,000). "1 AI credit = $0.01 USD"
  ([plans](https://docs.github.com/en/copilot/get-started/plans),
  [individual billing](https://docs.github.com/copilot/concepts/billing/usage-based-billing-for-individuals)).
  Verified maintainers of popular open-source projects may get Pro for
  free; that probably doesn't apply here.
- **Units changed:** GitHub now meters in **AI credits**, not "premium
  requests". Older guides that quote premium requests are out of date
  **[version]**.
- **Per-review cost:** about $0.05–1 at **Lite** effort and $0.25–5 at
  **Balanced**, which is the built-in default. Actions minutes are extra.
  With automatic review, "AI credits consumption is attributed" to the PR
  author
  ([code review concepts](https://docs.github.com/en/copilot/concepts/agents/code-review)).
- **Automatic review:** turn it on in your personal Copilot settings
  (Code review → Automatic Copilot code review). That covers pull requests
  you create in any repository where Copilot code review is available to
  you. Or use a branch **ruleset** with "Automatically request Copilot code
  review". Optional settings: review new pushes, review drafts
  ([configure automatic review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review)).
- **Mechanics:** agentic; it uses Actions runners for context gathering and
  tools. It comments rather than blocking, and by default its reviews "do
  not count toward required approvals". It is "not guaranteed to spot all
  problems". Model switching is not supported.
- **Custom instructions:** on GitHub.com, code review supports
  `.github/copilot-instructions.md`, path-specific
  `.github/instructions/**/*.instructions.md` (with `applyTo` globs and
  `excludeAgent: "code-review"` | `"cloud-agent"`), and "Agent instructions
  (using `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` or `REVIEW.md` files)". IDE
  surfaces support less
  ([support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support),
  [repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)).

### 1d. CodeRabbit

- **Pricing [plan]:** "Unlimited public repositories, no credit card
  required". "Open-source projects receive Team features with no paid
  subscription required". OSS rate limits are 1–10 PR reviews per developer
  per hour, varying with stars. **"For public repositories with less than
  10 stars, CodeRabbit requires reviews to be triggered manually"**
  ([plans](https://docs.coderabbit.ai/management/plans.md)).
  `robwise/dotfiles` has **1 star** (`gh repo view`, 2026-10-08), so in
  practice you would comment `@coderabbitai review` on each PR. The paid
  plans start at Essentials, $24/dev/mo billed annually
  ([pricing](https://www.coderabbit.ai/pricing)).
- **Config:** `.coderabbit.yaml` at the repo root. "The configuration
  present in the feature branch under review will be automatically detected
  and used"
  ([YAML config](https://docs.coderabbit.ai/getting-started/yaml-configuration.md)).
  `reviews.path_instructions` takes `path` globs and `instructions`
  ([path instructions](https://docs.coderabbit.ai/configuration/path-instructions.md)).
- **Custom pre-merge checks:** natural-language pass/fail rules, at most
  1,000 characters each, in `off`, `warning`, or `error` mode. "Available on
  the Team plan and above", which OSS projects get
  ([pre-merge checks](https://docs.coderabbit.ai/pr-reviews/pre-merge-checks)).
  This is a natural fit for "setup changed but docs did not".
- **Reads agent files by default:** `**/AGENTS.md`, `**/CLAUDE.md`,
  `**/GEMINI.md`, `**/AGENT.md`, `.github/copilot-instructions.md`,
  `.github/instructions/*.instructions.md`, Cursor/Windsurf/Cline rules.
  Each file is scoped to its own directory and subdirectories. Add more with
  `knowledge_base.code_guidelines.filePatterns`, for example
  `docs/agents/*.md`
  ([code guidelines](https://docs.coderabbit.ai/knowledge-base/code-guidelines)).
- **Auto-review defaults:** on, skips drafts, re-reviews each push, and has
  `ignore_usernames` for bots
  ([auto review](https://docs.coderabbit.ai/configuration/auto-review.md)).

### 1e. Other: OpenAI Codex review on GitHub (brief)

- Comment `@codex review`, or turn on **Automatic review** in Codex
  settings. On GitHub, Codex flags only P0 and P1 issues. Put rules under
  a `## Code Review Rules` heading in the nearest `AGENTS.md`
  ([Codex GitHub](https://learn.chatgpt.com/docs/third-party/github)).
- **[plan]** The Plus plan lists "Cloud-based integrations like automatic
  code review". The API-key option has "No cloud-based features (GitHub code
  review, Slack, etc.)"
  ([Codex pricing](https://learn.chatgpt.com/docs/pricing)). The pricing
  page doesn't say whether Free or Go plans include it.

---

## 2. How each picks up repository instructions

The repo has `AGENTS.md` (root), `GLOSSARY.md`, `docs/agents/*.md`, and
**no `CLAUDE.md`**. It also tracks `private_dot_codex/AGENTS.md`, a
**dotfile payload** (it deploys to `~/.codex/AGENTS.md`), not instructions
for this repo.

| Reviewer | Reads `AGENTS.md`? | Reads `CLAUDE.md` / `REVIEW.md`? | Follows `docs/agents/*.md`? | Instructions read from |
| - | - | - | - | - |
| claude-code-action, CLI session | **Yes.** Claude Code reads `AGENTS.md` when no `CLAUDE.md` exists, from v2.1.277; the action pins 2.1.295 ([memory](https://code.claude.com/docs/en/memory#agents-md)) | `CLAUDE.md` yes; `REVIEW.md` not documented | Only if the prompt or `AGENTS.md` tells it to open them | `CLAUDE.md` and `.claude/` are **restored from the base branch**; `AGENTS.md` is **not** in that list, so it comes from the **PR head** ([security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md), [`SENSITIVE_PATHS`](https://github.com/anthropics/claude-code-action/blob/2dca132ff0e0c4094ce6048b422c6915a071210b/src/github/operations/restore-config.ts)) |
| claude-code-action + stock `code-review` plugin | Session loads it, but the plugin's compliance step looks only for `CLAUDE.md` (§1a) | `CLAUDE.md` only | No | Same as above |
| Managed Code Review | Not documented | `CLAUDE.md` (violations are nits) and `REVIEW.md` (review-only rules) | Not documented | Not documented |
| Copilot code review | **Yes**; "the nearest `AGENTS.md` file in the directory tree will take precedence" | Yes: a root `CLAUDE.md`, and `REVIEW.md` | Not documented | "Copilot reads … from the **head branch**" |
| CodeRabbit | **Yes** (`**/AGENTS.md`, directory-scoped) | `**/CLAUDE.md` yes; `REVIEW.md` not in the default list | Only if you add `filePatterns` | `.coderabbit.yaml` from the **feature branch** |
| Codex | **Yes** (`## Code Review Rules` in the nearest `AGENTS.md`) | Not documented | Not documented | Not documented |

**Configuration needed beyond the repo:**

- **Action:** none for `AGENTS.md`. The rule in `AGENTS.md` says only
  "update both documents"; it doesn't define drift. Spell out the drift
  checks in the workflow `prompt` or a skill (my recommendation).
  - A skill in `.claude/skills/` comes from the base branch (`.claude/` is
    restored from base), so a new review skill can't run on the PR that adds
    it.
  - A PR-authored `.claude/` is kept under `.claude-pr/` "for reference
    only".
  - With the default App auth, the workflow file must match the default
    branch (see §4), so the review workflow can't review the PR that adds
    it either.
- **Copilot / CodeRabbit:** work from `AGENTS.md` as is. Docs-drift rules
  are more reliable as explicit path instructions: CodeRabbit
  `path_instructions` or a pre-merge check; Copilot
  `.github/instructions/docs-drift.instructions.md` with `applyTo`
  (my recommendation).
- **`.claude/skills/` by tool:**
  - **Action:** loads project skills from the base branch's `.claude/` and
    runs them by `/skill-name` in `prompt`.
  - **Copilot:** project skills live in "`.github/skills`, `.claude/skills`,
    or `.agents/skills`", and "Agent skills work with … Copilot code review"
    ([agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)).
    Copilot reads them from the head branch. Exactly when code review
    chooses to use a skill is not documented in what I read.
  - **CodeRabbit:** `.claude/skills` is not in its default guideline
    patterns. Add it to `filePatterns` if wanted.
  - **Managed Code Review / Codex:** not documented.
  - **`docs/agents/*.md`:** no tool loads these automatically. Each needs the
    prompt, `AGENTS.md`, or a pattern to point at them.
- **Nested `AGENTS.md` gotcha (my inference from the scoping rules above):**
  Copilot, CodeRabbit, Codex, and Claude Code (when it reads files in that
  directory) will treat `private_dot_codex/AGENTS.md` as instructions for
  files under `private_dot_codex/`. Today it is one harmless line. Keep that
  in mind if it grows.
- **chezmoi:** dot-prefixed source paths are ignored ("chezmoi ignores all
  files and directories in the source directory that begin with a `.`",
  [chezmoi](https://www.chezmoi.io/reference/source-state-attributes/)), so
  `.github/`, `.claude/`, and `.coderabbit.yaml` stay out of `~`. A root
  `CLAUDE.md` or `REVIEW.md` is **not** dot-prefixed. Add it to
  `.chezmoiignore` (as `AGENTS.md` already is), or it deploys to
  `~/CLAUDE.md` and loads into every Claude Code session under `~`.

---

## 3. Expected cost for this repo (~10–15 PRs/month)

| Option | Marginal monthly cost | Notes |
| - | - | - |
| Action + `CLAUDE_CODE_OAUTH_TOKEN` | **$0 extra**; uses Pro/Max plan limits | Actions minutes free on public repo ([billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)). Runs compete with your interactive use for the plan's usage windows ([costs](https://code.claude.com/docs/en/costs)) |
| Action + `ANTHROPIC_API_KEY` | Pay per token | Sonnet 5: $2 in / $10 out per MTok; Opus 5.5: $4 / $20 ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)). **My rough estimate, unmeasured:** a small dotfiles PR with ~300k input tokens across turns (much of it cached) and ~10k output on Sonnet 5 costs well under $1 per review, so roughly $5–10/month. Measure the first runs from the run log; cap with `--max-turns` and `--model` |
| Managed Code Review | n/a on Pro/Max; ~$15–25 per review on Team/Enterprise | Would be ~$150–375/month here |
| Ultrareview | 3 free runs, then $5–25 per review | Manual escalation, not per-PR |
| Copilot Pro | $10/mo if you don't already have it; reviews draw from 1,500 credits ($15) | 12 Lite reviews ≈ $0.60–12; 12 Balanced ≈ $3–60, which can exhaust the allowance. Per GitHub, when the member's quota is exhausted the review fails (paraphrased from the automatic-review page). Actions minutes for public repos are *likely* $0 (inferred from the Actions billing rule; GitHub's Copilot page doesn't say) |
| CodeRabbit OSS | $0 | Manual trigger until the repo has 10 stars |
| Codex | Included in Plus or higher, within usage limits | Not stated for Free/Go |

---

## 4. Security for a public repo

**Sourced facts**

- On `pull_request` from a **fork**, "secrets are not passed to the runner"
  and "The `GITHUB_TOKEN` has read-only permissions". First-time
  contributors may need maintainer approval to run workflows
  ([events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)).
  Anthropic: "the review runs only on pull requests from branches in the
  same repository"
  ([docs](https://code.claude.com/docs/en/github-actions#run-a-skill)).
- `pull_request_target` "runs in the context of the default branch of the
  base repository" with secrets. "Avoid using this event if you need to
  build or run code from the pull request." Workflows using it "must not
  explicitly check out untrusted code"
  ([events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
  [secure use](https://docs.github.com/en/actions/reference/security/secure-use)).
  Anthropic: "Do not check out an untrusted ref into the workspace root
  before this action"
  ([security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)).
- **Least privilege:** grant `GITHUB_TOKEN` the minimum permissions; pin
  third-party actions to a full commit SHA, which "is currently the only way
  to use an action as an immutable release"
  ([secure use](https://docs.github.com/en/actions/reference/security/secure-use)).
- **Action guards:** the action requires a human actor with write access.
  Keep `allowed_bots` and `allowed_non_write_users` unset. On public repos,
  `allowed_bots: '*'` lets any GitHub App invoke it.
  `show_full_output` must stay off, because "These logs are publicly visible
  in GitHub Actions for public repositories!"
  ([security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)).
- **Prompt injection:** the action strips HTML comments, invisible
  characters, image alt text, and hidden attributes, but "new bypass
  techniques may emerge"
  ([security.md](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)).
  Claude Code's own memory docs say instructions are "context, not enforced
  configuration"
  ([memory](https://code.claude.com/docs/en/memory)).

**Applied to this repo (my analysis)**

- Every PR so far (#1–#4) was opened by `robwise` from a branch in
  `robwise/dotfiles` (`gh api …/pulls`, 2026-10-08). `pull_request` with
  secrets therefore works, and fork PRs fail closed because they get no
  secret.
  - Add `if: github.event.pull_request.head.repo.full_name == github.repository`
    so fork PRs skip cleanly instead of erroring.
- **The PR can steer its own reviewer, partly.** With `pull_request`, the
  workflow runs on the merge ref (`GITHUB_SHA` = "Last merge commit").
  - **Workflow file:** under the action's **default App auth**, Anthropic's
    token exchange rejects a workflow file that differs from the default
    branch, and the action then *skips*. The test fixture message reads:
    "The workflow file must exist and have identical content to the version
    on the repository's default branch"
    ([token.ts](https://github.com/anthropics/claude-code-action/blob/2dca132ff0e0c4094ce6048b422c6915a071210b/src/github/token.ts),
    [token.test.ts](https://github.com/anthropics/claude-code-action/blob/2dca132ff0e0c4094ce6048b422c6915a071210b/test/token.test.ts)).
    So a PR can't edit the workflow or prompt to change its own review. It
    gets no review instead, and you should treat that as a signal. Merge the
    workflow to `main` before opening any test PRs.
  - **Instructions:** the action still reads `AGENTS.md` from PR head.
  Copilot and CodeRabbit read their instructions from the head or feature
  branch. For a solo repo with your own agents this is acceptable. Treat a
  PR that edits `AGENTS.md`, `.github/`, `.coderabbit.yaml`, or
  `docs/agents/` as one you read yourself.
- **Agent-authored PRs carry indirect-injection risk.** If an authoring
  agent read hostile web content, the injected text can reach the reviewer
  through the diff. Keep the review job read-mostly:
  - `contents: read`, `pull-requests: write` (for comments), `id-token: write`
  - `--allowedTools` limited to the inline-comment tool, `gh pr view`,
    `gh pr diff`, and `gh pr comment`
  - no `Write` or `Edit`, and no unrestricted Bash
- **App token vs `GITHUB_TOKEN` (verify before relying on it):** without
  `github_token`, the action posts with a Claude App token minted through
  Anthropic's token exchange
  ([token.ts](https://github.com/anthropics/claude-code-action/blob/2dca132ff0e0c4094ce6048b422c6915a071210b/src/github/token.ts)).
  The workflow's `permissions:` block scopes `GITHUB_TOKEN`, not that App
  token. The App's install-time permission set is broad, including
  Workflows and Actions write
  ([App permissions](https://code.claude.com/docs/en/github-actions#github-app-permissions)).
  Passing `github_token: ${{ secrets.GITHUB_TOKEN }}` bypasses the exchange
  in source. That narrows GitHub permissions to the job's `permissions:`,
  but it **also drops the workflow-must-match-default-branch check** above.
  It is a trade-off, not a free win. Whether the whole review flow works
  without the App installed is untested here. *My lean for this repo:* keep
  the default App auth, since the workflow-integrity check matters more than
  the narrower token.
- **Which options store no secret in the repo:**
  - Copilot code review, CodeRabbit, managed Code Review, and Codex all run
    as GitHub Apps or integrations with no repo secret.
  - The Action can avoid a static Anthropic secret only through workload
    identity federation (API billing) or a cloud provider via OIDC. A
    subscription token is always a stored secret.

---

## 5. Evaluating and tuning the reviewer

**What vendors say (sourced)**

- **Anthropic Code Review:** every comment comes with 👍/👎, and Anthropic
  "uses them to tune the reviewer". In `REVIEW.md`, recalibrate severity,
  cap nits, add skip rules, set a verification bar ("behavior claims need a
  `file:line` citation"), and limit re-review churn
  ([Code Review](https://code.claude.com/docs/en/code-review#customize-reviews)).
  These levers carry over to a custom Action prompt.
- **Anthropic eval guidance:** "Be task-specific … Don't forget to factor in
  edge cases", "Automate when possible", "Prioritize volume over quality"
  ([develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)).
- **`/code-review` effort:** at `low` "you see fewer false positives"; higher
  levels broaden coverage
  ([Code Review](https://code.claude.com/docs/en/code-review#tune-effort-and-arguments)).
- **Copilot:** "click the thumbs up (:+1:) or thumbs down (:-1:) button" on a
  review comment. On re-review, "Copilot may repeat the same comments again,
  even if they have been downvoted"
  ([use code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)).
- **CodeRabbit:** learns from `@coderabbitai` chat ("learnings"), and you
  can dry-run a rule with `@coderabbitai evaluate custom pre-merge check`
  ([knowledge base](https://docs.coderabbit.ai/integrations/knowledge-base),
  [pre-merge checks](https://docs.coderabbit.ai/pr-reviews/pre-merge-checks)).

**Lightweight practice for a solo repo (my recommendation)**

1. **Seed 4–5 throwaway PRs** from a branch, one defect each:
   - (a) add a package to `.chezmoidata/packages.toml` or `dot_Brewfile`
     without an inventory entry;
   - (b) remove a config file but leave its inventory and usage entries;
   - (c) change an alias in `dot_zshrc` so `docs/usage.md` describes the old
     behavior;
   - (d) a clean control PR that updates both docs correctly;
   - (e) a docs-only PR.

   Open them only after the review workflow is on `main` (see §4).
   Expected: (a)–(c) flagged on the right line, (d) and (e) get "no drift
   found". Close them unmerged. Mark them non-draft, because drafts are
   skipped by the stock plugin and by default by Copilot and CodeRabbit.
2. **Score each run:** caught or missed, plus false positives per PR. Keep a
   small table in the Linear ticket that tracks this work. Rerun the seeds
   whenever you change the prompt or model, or the action's major version.
3. **Track real PRs for a month:** for each finding, record useful, wrong,
   or noise (👍/👎 is enough). If noise exceeds about one per PR, tighten
   the prompt: require a quoted doc line and a quoted setup line for every
   drift claim, and cap non-drift nits.
4. **Re-review on push:** confirm a fix commit gets re-reviewed. With the
   stock plugin it won't (§1a).

---

## 6. Comparison and recommendation

| | Setup effort | Cost here | Reads `AGENTS.md`? | Inline comments? | Secret in repo? | Fork-PR safety |
| - | - | - | - | - | - | - |
| **claude-code-action, custom prompt, OAuth token** | Medium: one workflow and one secret (or `/install-github-app`, then replace the review prompt) | $0 extra (Pro/Max limits) | Yes (CLI, ≥2.1.277) | Yes (MCP tool) | Yes (`CLAUDE_CODE_OAUTH_TOKEN`, 1-yr) | Safe on `pull_request`: forks get no secret, so the job skips. Unsafe if moved to `pull_request_target` with a PR checkout |
| claude-code-action, stock `code-review` plugin | Low (`/install-github-app`) | Same | Session yes, plugin logic no (`CLAUDE.md` only) | Yes | Yes | Same |
| Managed Claude Code Review | Low (admin toggle) | Unavailable on Pro/Max; ~$15–25 per review | Not documented (`CLAUDE.md` + `REVIEW.md`) | Yes, plus a check run | No | Forks only on `@claude review` by a writer |
| `/code-review --comment` run locally by the authoring agent | Low (an `AGENTS.md` step) | Plan usage | Yes | Yes | No | n/a (local) |
| Copilot code review | Low (toggle or ruleset) | Needs Copilot Pro or higher ($10/mo+); ~$0.05–1/review at Lite | Yes (also `CLAUDE.md`/`REVIEW.md`) | Yes | No | Managed by GitHub; reads instructions from head |
| CodeRabbit (OSS) | Low (install the app, optional `.coderabbit.yaml`) | $0 | Yes | Yes | No | Managed; config from feature branch; **manual trigger under 10 stars** |
| Codex review | Low (connect the repo) | ChatGPT Plus or higher | Yes (`## Code Review Rules`) | Yes (P0/P1 only) | No | Managed |

### Recommendation (mine, not a vendor claim)

1. **Start with claude-code-action, an OAuth token, and a custom docs-drift
   prompt.** It costs nothing beyond your plan, reads `AGENTS.md`, posts
   inline, and you control the prompt.
   - Run `/install-github-app` for the App and secret. Then replace the
     generated review workflow's `prompt` with one that:
     - reads `AGENTS.md`, `GLOSSARY.md`, `docs/inventory.md`, and
       `docs/usage.md`;
     - maps changed setup files (`dot_*`, `private_dot_*`, `run_*`,
       `.chezmoidata/packages.toml`, `dot_Brewfile`, `.chezmoiignore`,
       `fonts/`) to their doc entries;
     - reports three drift classes (missing entry, wrong explanation, stale
       entry for removed setup), each with quoted lines;
     - optionally adds a short general-correctness pass, capped at a few
       high-confidence findings;
     - posts inline, or one "no drift found" comment;
     - on re-runs (`synchronize`), reads existing Claude comments first,
       doesn't repeat a finding already posted, and says in the summary
       which earlier findings are now fixed. Without this, every push
       reposts the same findings. `use_sticky_comment` in
       [action.yml](https://github.com/anthropics/claude-code-action/blob/main/action.yml)
       may help keep one summary comment; verify that it applies in
       automation mode.
   - Workflow settings: triggers `[opened, synchronize, ready_for_review,
     reopened]`; the same-repo `if:` guard; least-privilege `permissions:`;
     `--allowedTools` limited to read and comment tools; `--max-turns`;
     `timeout-minutes`; a `concurrency` group per PR; pin the action to a
     SHA.
   - Keep `@claude` (interactive `claude.yml`) for on-demand follow-ups.
2. **Validate with the seeded PRs (§5)** before you trust silence. Merge
   the workflow to `main` first, because App auth skips a PR whose workflow
   differs from the default branch.
3. **Optional second reviewer:** if you already have Copilot Pro, turn on
   automatic Copilot review with **Lite** effort. It reads `AGENTS.md` with
   no secret and catches general issues. Skip CodeRabbit until the repo
   passes 10 stars, unless you don't mind typing `@coderabbitai review`.
4. **Escalation:** for a big refactor, run `/code-review ultra <PR> --post`
   (3 free runs on Pro/Max).
5. **Do it as a setup change:** add the workflow, plus entries in
   `docs/inventory.md` (the workflow, the secret, and the GitHub App) and
   `docs/usage.md` (how to read, re-trigger, and tune the review), per
   `AGENTS.md`. Only if you add a root `REVIEW.md` or `CLAUDE.md`, also add
   it to `.chezmoiignore`.

---

## Sources

All accessed 2026-10-08.

**Anthropic**

- Claude Code GitHub Actions: <https://code.claude.com/docs/en/github-actions>
- Claude Code Review (managed) and `/code-review`: <https://code.claude.com/docs/en/code-review>
- Ultrareview: <https://code.claude.com/docs/en/ultrareview>
- Authentication (`claude setup-token`): <https://code.claude.com/docs/en/authentication>
- Memory / AGENTS.md: <https://code.claude.com/docs/en/memory>
- Environment variables (feature flags, first session): <https://code.claude.com/docs/en/env-vars>
- Costs: <https://code.claude.com/docs/en/costs>
- API pricing: <https://platform.claude.com/docs/en/about-claude/pricing>
- Develop tests (evals): <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests>
- claude-code-action repo: <https://github.com/anthropics/claude-code-action>
  - security.md: <https://github.com/anthropics/claude-code-action/blob/main/docs/security.md>
  - solutions.md: <https://github.com/anthropics/claude-code-action/blob/main/docs/solutions.md>
  - action.yml: <https://github.com/anthropics/claude-code-action/blob/main/action.yml>
  - source at `2dca132` (`src/github/token.ts`, `src/github/operations/restore-config.ts`, `base-action/action.yml`, `base-action/src/parse-sdk-options.ts`)
- `code-review` plugin source (anthropics/claude-code at `602df92`): <https://github.com/anthropics/claude-code/blob/602df92bf481ed904533e95c09f740f40aab5aed/plugins/code-review/commands/code-review.md>

**GitHub**

- Copilot code review concepts: <https://docs.github.com/en/copilot/concepts/agents/code-review>
- Configure automatic review: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review>
- Use code review (feedback): <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review>
- Copilot plans: <https://docs.github.com/en/copilot/get-started/plans>
- Usage-based billing for individuals: <https://docs.github.com/copilot/concepts/billing/usage-based-billing-for-individuals>
- Custom instructions support matrix: <https://docs.github.com/en/copilot/reference/custom-instructions-support>
- Repository custom instructions: <https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions>
- Actions billing: <https://docs.github.com/en/billing/concepts/product-billing/github-actions>
- Events that trigger workflows: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>
- Secure use reference: <https://docs.github.com/en/actions/reference/security/secure-use>

**CodeRabbit**

- Pricing: <https://www.coderabbit.ai/pricing>
- Plans: <https://docs.coderabbit.ai/management/plans.md>
- YAML configuration: <https://docs.coderabbit.ai/getting-started/yaml-configuration.md>
- Path instructions: <https://docs.coderabbit.ai/configuration/path-instructions.md>
- Code guidelines: <https://docs.coderabbit.ai/knowledge-base/code-guidelines>
- Knowledge base: <https://docs.coderabbit.ai/integrations/knowledge-base>
- Auto review: <https://docs.coderabbit.ai/configuration/auto-review.md>
- Pre-merge checks: <https://docs.coderabbit.ai/pr-reviews/pre-merge-checks>

**OpenAI**

- Codex GitHub integration: <https://learn.chatgpt.com/docs/third-party/github>
- Codex pricing: <https://learn.chatgpt.com/docs/pricing>

**Other**

- chezmoi source state attributes: <https://www.chezmoi.io/reference/source-state-attributes/>
- Repo facts (stars, PR authors) from `gh repo view` and `gh api repos/robwise/dotfiles/pulls`
