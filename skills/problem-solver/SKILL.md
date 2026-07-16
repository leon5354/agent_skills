---
name: problem-solver
description: Structured problem-solving workflow with a local knowledge base. When encountering an error, bug, or unknown issue, search the knowledge base first before trial-and-error. If not found, search the web, then debug from scratch. Always log new solutions to the knowledge base for future reference. Use when hitting errors, bugs, unexpected behavior, dependency conflicts, build failures, or any technical challenge. Triggers on "error", "bug", "crash", "not working", "failed", "stuck", "how to fix", "what causes".
---

# Problem Solver

Don't guess. Don't trial-and-error. **Search first, solve second, log always.**

Like a developer checking Stack Overflow before writing code: check the knowledge base, then the web, then debug.

## Workflow

```
Hit problem
  │
  ├→ Step 1: Search knowledge base (cheap, instant)
  │   └→ Found? Apply solution. Done.
  │
  ├→ Step 2: Search the web
  │   └→ Found? Apply + log to knowledge base. Done.
  │
  ├→ Step 3: Debug from scratch
  │   └→ Solved? Log to knowledge base. Done.
  │
  └→ Still stuck? Escalate to user with full context.
```

## Step 1: Search Knowledge Base

Read `knowledge-base/index.md` — it is a lightweight keyword table. Cheap to scan.

```bash
# Search by keyword in index
grep -i "<keyword>" knowledge-base/index.md
```

If a matching entry ID is found (e.g., `P003`), read the full entry:

```bash
cat knowledge-base/entries/P003.md
```

Apply the documented solution. If it works, done.

## Step 2: Search the Web

If knowledge base has no match, search the web with specific error messages:

```
"<exact error message>" <technology> <version> site:stackoverflow.com
```

If found, apply the solution, then **log it** (Step 4).

## Step 3: Debug From Scratch

If no web results help, debug methodically:

1. Reproduce the error consistently
2. Isolate the minimal failing case
3. Check: dependencies, versions, paths, permissions, environment variables
4. Read official docs for the failing component
5. Try one fix at a time (not multiple at once)
6. Document each attempt and its result

## Step 4: Log to Knowledge Base (MANDATORY)

Every time a problem is solved (from any source), create a knowledge base entry.

### Create Entry

Copy the template from `references/entry-template.md`:

```bash
cp references/entry-template.md knowledge-base/entries/P<NNN>.md
```

Fill in all sections. Then update the index:

### Update Index

Append a row to `knowledge-base/index.md`:

```markdown
| P<NNN> | <keywords> | <one-line summary> | <technologies> |
```

### Entry Naming

- Sequential: P001, P002, P003...
- Check `knowledge-base/entries/` for the next available number
- Never reuse or recycle numbers

## Knowledge Base Structure

```
knowledge-base/
├── index.md              # Lightweight keyword table (always scan this first)
└── entries/
    ├── P001.md           # Individual problem-solution entries
    ├── P002.md
    └── ...
```

## Design Principles

1. **Token-friendly:** Index is a flat table. Only load entries you need.
2. **Keyword-driven:** Index by error keywords, technology names, and symptoms.
3. **Searchable:** Use grep on index.md, not LLM reasoning, to find matches.
4. **Cumulative:** Every solved problem makes the next occurrence instant.
5. **Cross-referenced:** Link related entries with `See also: P0XX`.

## When to Escalate to User

If all three steps fail:
- Summarize the problem
- List what was tried and why it failed
- Propose 2-3 next steps with trade-offs
- Ask the user to choose

Do not loop indefinitely. Three failed approaches = escalate.
