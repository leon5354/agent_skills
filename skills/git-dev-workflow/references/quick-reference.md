# GitHub Development Workflow Reference

## Branch Types

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feat/` | New feature or enhancement | `feat/audio-separator-module` |
| `fix/` | Bug fix | `fix/demucs-memory-leak` |
| `docs/` | Documentation only | `docs/api-reference` |
| `refactor/` | Code restructuring, no behavior change | `refactor/pipeline-architecture` |
| `test/` | Test additions or fixes | `test/transcriber-integration` |
| `chore/` | Build, CI, tooling, dependencies | `chore/setup-pyinstaller` |

## PR Template

```markdown
## Summary
<1-2 sentences>

## Changes
- Specific change 1
- Specific change 2

## Documentation Updated
- [ ] CHANGELOG.md
- [ ] README.md
- [ ] API docs
- [ ] Architecture docs
- [ ] Other: <specify>

## Testing
- [x] All tests pass
- [x] New tests added for new functionality

## Breaking Changes
<None, or describe migration steps>

## Related Issues
<Close #123, Refs #456, or "N/A">
```

## SemVer Guide

| Version | When to bump | Example |
|---------|-------------|---------|
| Major (1.0.0 → 2.0.0) | Breaking changes | API removal, pipeline restructure |
| Minor (1.0.0 → 1.1.0) | New features, backward compatible | New output format, new preset |
| Patch (1.0.0 → 1.0.1) | Bug fixes | Fix crash, fix wrong note |

Pre-release: `0.x.y` while in active development before 1.0 stable.
