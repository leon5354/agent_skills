# Update Docs Skill

Auto-updates `CHANGELOG.md` and related docs on every commit.

## What It Does

- Reads the staged commit message before each commit (pre-commit hook)
- Prepends a dated entry to `CHANGELOG.md`
- Stages the updated changelog so it's included in the commit

## Setup (per project)

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

## Usage

```python
from skills.update_docs.skill import UpdateDocsSkill

skill = UpdateDocsSkill(repo_path="/path/to/repo")
skill.run()
```

Or run directly as the pre-commit hook — no import needed.

## Output

Each commit prepends an entry to `CHANGELOG.md`:

```
## 2026-07-11 — Add Z.AI GLM-5.2 as primary provider

---
```

## Notes

- Uses `utf-8-sig` encoding to handle Windows cp950 terminals
- Reads commit message from `.git/COMMIT_EDITMSG` (available during pre-commit)
- Safe to skip: errors are caught and printed, never block the commit
