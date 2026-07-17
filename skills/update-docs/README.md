# Update Docs Skill

Manages project documentation lifecycle: auto-changelog on every commit + document status header sync.

## What It Does

### 1. Auto-Changelog (pre-commit hook)

- Reads the commit message before each commit
- Prepends a dated entry to `CHANGELOG.md`
- Stages the updated changelog so it's included in the commit

### 2. Document Status Header Sync (manual / CI)

Every project document should have a standardized metadata header:

```markdown
> **Status**: <Draft | Prototype | Alpha | Beta | Stable | Deprecated>
> **Updated**: YYYY-MM-DD
> **Reflects**: <commit hash, PR number, or version tag>
```

And a document changelog at the bottom:

```markdown
## Document Changelog

| Date | Change | Source |
|------|--------|--------|
| 2026-07-17 | Initial version | PR #1 |
```

Use `update_status_header()` to programmatically update these fields.

## Setup (per project)

### Auto-Changelog Hook

1. Copy `skill.py` to your project as `scripts/update_changelog.py`
2. Create `.githooks/pre-commit`:
   ```sh
   #!/bin/sh
   python "$(git rev-parse --show-toplevel)/scripts/update_changelog.py"
   ```
3. Point git at it:
   ```sh
   git config core.hooksPath .githooks
   ```

### Status Header Management

```python
from skills.update_docs.skill import UpdateDocsSkill

skill = UpdateDocsSkill(repo_path="/path/to/repo")

# Update a document's status header
skill.update_status_header(
    filepath="PLAN.md",
    status="Prototype",
    reflects="PR #5",
    change_description="Synced model names, added pre-analysis pass"
)

# Auto-changelog (pre-commit hook)
skill.run()
```

## Output

### CHANGELOG.md (auto, every commit)

```
## 2026-07-17 — feat: add pre-analysis pass design

---
```

### Document Status Header (manual/CI)

```
> **Status**: Prototype
> **Updated**: 2026-07-17
> **Reflects**: PR #5
```

## Why Status Headers?

Without status headers, documents go stale silently. A PLAN.md written during design phase still references dropped libraries 3 PRs later. The status header forces every PR to answer: "Does this PR invalidate any document?" If yes, update the document's `Reflects` field and content in the same PR.

## Notes

- Uses `utf-8-sig` encoding to handle Windows cp950 terminals
- Reads commit message from `.git/COMMIT_EDITMSG` (available during pre-commit)
- Safe to skip: errors are caught and printed, never block the commit
- `update_status_header()` is idempotent: safe to call multiple times
- If a document has no status header, `update_status_header()` will add one after the first `---` separator or after the title
