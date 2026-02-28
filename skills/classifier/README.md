# Classifier Skill

Text classification using LLM reasoning.

## What It Does

- Assigns topics to text based on known categories
- Detects when text doesn't fit any known topic
- Suggests new category names for uncategorized content
- Includes sentiment and confidence scoring

## Usage

```python
from skills.classifier.skill import ClassifierSkill

# Initialize with your topics
classifier = ClassifierSkill(topics=[
    "Product Quality",
    "Customer Service", 
    "Pricing"
])

# Classify text
result = classifier.classify("The product broke after 2 days")

print(result.labels)      # ["Product Quality"]
print(result.sentiment)   # "negative"
print(result.confidence)  # 0.9
```

## Output Structure

```python
Result:
    labels: List[str]           # Matched topics
    sentiment: str              # positive/negative/neutral/mixed
    confidence: float           # 0.0 - 1.0
    suggested_label: str        # New topic name (if UNCATEGORIZED)
    suggestion_reason: str      # Why this is a new category
```

## Configuration

Edit `config.py`:

```python
MASTER_TOPICS = ["Your", "Custom", "Topics"]
MIN_CONFIDENCE = 0.7
TEMPERATURE = 0.1
```

## How It Works

1. Builds a prompt with known topics
2. Sends text to LLM for classification
3. Parses JSON response
4. Returns structured result

## Dependencies

- `llm-wrapper` skill
- `pydantic` for data validation
