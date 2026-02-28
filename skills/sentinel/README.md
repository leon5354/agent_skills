# Sentinel Skill

Dynamic topic discovery agent.

## What It Does

- Monitors classification results for new topic suggestions
- Counts how often each suggestion appears
- Promotes topics to the main list when threshold reached
- Logs all discoveries with sample texts

## Usage

```python
from skills.sentinel.skill import SentinelSkill

# Initialize with threshold
sentinel = SentinelSkill(threshold=5)

# Observe suggestions
promoted = sentinel.observe("Pacing Issues", "The pacing was slow...", idx=0)

if promoted:
    print("New topic discovered!")

# Check status
print(sentinel.status())
```

## How Discovery Works

```
Hit 1: "Pacing Issues"  [░░░░░] 1/5
Hit 2: "Pacing Issues"  [██░░░] 2/5
Hit 3: "Pacing Issues"  [███░░] 3/5
Hit 4: "Pacing Issues"  [████░] 4/5
Hit 5: "Pacing Issues"  [█████] 5/5 → PROMOTED!
```

## Configuration

Edit `config.py`:

```python
DISCOVERY_THRESHOLD = 5    # Hits needed to promote
SENTINEL_LOG_FILE = "output/sentinel_log.json"
```

## Output

When a topic is promoted:

```json
{
  "topic": "Pacing Issues",
  "hits": 5,
  "first_seen": "2026-02-28T10:00:00",
  "promoted_at": "2026-02-28T12:30:00",
  "samples": [
    "The pacing was so slow...",
    "Movie dragged on forever..."
  ]
}
```

## Methods

| Method | Purpose |
|--------|---------|
| `observe(topic, text, idx)` | Log a suggestion |
| `get_pending()` | Topics not yet promoted |
| `get_confirmed()` | Promoted topics |
| `get_indices(topic)` | Row indices for re-tagging |
| `status()` | Human-readable summary |
