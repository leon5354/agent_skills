# How to Add Entries

1. Check `entries/` for the highest P-number
2. Copy `references/entry-template.md` to `entries/P<NNN>.md`
3. Fill in ALL sections (Problem, Error, Environment, Root Cause, Solution, Prevention, Keywords)
4. Append a row to `index.md` with keywords and summary
5. Add cross-references to related entries if applicable

## Index Format

```
| P00X | keyword1 keyword2 keyword3 | short problem description | tech stack |
```

## Rules

- One problem per entry
- Keywords must include: error keywords, technology name, symptom
- Root Cause is mandatory (not just the fix)
- Source must credit where the solution came from
- Mark status as Resolved only after verified working
