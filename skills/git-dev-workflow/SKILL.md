---
name: git-dev-workflow
description: GitHub development workflow for project development. Enforces strict git best practices from branch creation to PR to squash merge. Requires all documentation (CHANGELOG, README, docs) stay synced with code changes at every step. Use when developing features, fixing bugs, or making any code changes in a GitHub-hosted project. Triggers on "develop", "new feature", "fix bug", "create branch", "open PR", "git workflow", "start coding", "implement".
---

# Git Development Workflow

Strict GitHub development workflow. Every code change follows the full pipeline: branch → develop → test → docs → commit → PR → squash merge. No shortcuts.

## Golden Rules

1. **Never commit to `main` directly.** Always use feature branches.
2. **All documentation stays synced.** Every PR must update relevant docs.
3. **English only** for code, comments, commit messages, PR descriptions, and documentation.
4. **One PR = one logical change.** Don't mix unrelated features.
5. **Squash and merge.** Clean commit history on `main`.
6. **Every commit has a clear message.** What was done + why. No vague messages.
7. **Every commit has inline comments** for non-obvious logic.
8. **Tests run before every commit.** No committing broken code.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository initialized with `main` as default branch
- `.gitignore` configured for the project

## Workflow Steps

### Step 1: Sync Main

```bash
git checkout main
git pull origin main
```

Always start from latest `main`.

### Step 2: Create Feature Branch

```bash
git checkout -b feat/<short-description>
# or
git checkout -b fix/<short-description>
```

Branch naming convention:
- `feat/` — new features
- `fix/` — bug fixes
- `docs/` — documentation only
- `refactor/` — code refactoring
- `test/` — test additions

### Step 3: Develop

Write code. Commit frequently locally with clear messages.

**Commit message rules:**
- Every commit must explain WHAT was done and WHY
- Format: `<type>: <imperative description>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

```bash
# Good
git commit -m "feat: add Demucs separator with configurable model selection"
git commit -m "fix: handle empty audio input without crashing"
git commit -m "test: add unit tests for Basic Pitch wrapper"

# Bad (too vague)
git commit -m "update"
git commit -m "fix bug"
git commit -m "WIP"
```

**Every commit must include:**
1. Clear commit message (what + why)
2. Inline code comments for non-obvious logic
3. If adding/changing functionality: corresponding test in the same commit

**Before each commit, run tests:**

```bash
# Run affected tests before committing
pytest tests/test_<module>.py -v

# Or full suite if broad changes
pytest tests/ -v
```

Do NOT commit if tests fail. Fix first, then commit.

### Step 4: Sync Documentation (MANDATORY)

Before opening PR, update ALL related documentation:

- [ ] **CHANGELOG.md** — add entry under `[Unreleased]`
- [ ] **README.md** — update if features/installation/usage changed
- [ ] **API docs** — update if API surface changed
- [ ] **Architecture docs** — update if structure changed
- [ ] **Inline comments** — update for complex logic
- [ ] **Docstrings** — all public functions/classes

If documentation is not updated, the PR is incomplete. No exceptions.

### Step 5: Test

```bash
# Run full test suite
pytest tests/ -v

# Or project-specific test command
```

All tests must pass. If adding new features, add tests.

### Step 6: Push and Open PR

```bash
git push -u origin feat/<short-description>
```

Open PR via GitHub CLI:

```bash
gh pr create \
  --title "feat: <concise description>" \
  --body "$(cat <<'EOF'
## Summary
<1-2 sentences describing what this PR does>

## Changes
- <bullet list of specific changes>

## Documentation Updated
- [ ] CHANGELOG.md
- [ ] README.md
- [ ] Other: <specify>

## Testing
- [x] All tests pass
- [x] New tests added for new functionality

## Notes
<any additional context, breaking changes, migration steps>
EOF
)"
```

PR title format: `<type>: <description>` (e.g., `feat: add Demucs separator module`)

### Step 7: Review and Squash Merge

After approval:

```bash
# Squash and merge via CLI
gh pr merge <PR_NUMBER> --squash --delete-branch

# Or via GitHub web UI: "Squash and merge" button
```

Squash commit message format:

```
feat: <description>

- <key change 1>
- <key change 2>
- <key change 3>
```

### Step 8: Cleanup

```bash
git checkout main
git pull origin main
git branch -d feat/<short-description>  # local cleanup
```

## CHANGELOG Format

```markdown
# Changelog

## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior of Y

### Fixed
- Bug Z resolved

### Removed
- Deprecated W removed
```

Use [Keep a Changelog](https://keepachangelog.com/) format. Version numbers follow [SemVer](https://semver.org/).

## Commit Message Conventions

### Squash Commit (final, on main)

```
<type>: <imperative description>

- <change detail>
- <change detail>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

### WIP Commits (intermediate, on branch)

```
<type>: <what you did>
```

Still needs a clear message. `WIP` alone is not acceptable. These get squashed away but must still be readable in PR review.

## Branch Protection Rules (recommended for repo)

- Require PR before merging to `main`
- Require squash merge
- Require status checks to pass
- Require at least 1 approval (for team projects)

## Quick Reference

```
main → pull → branch → develop → docs → test → push → PR → squash merge → cleanup
```

Every step. Every time. No skipping.
