# LLM-Agent Demo

A demonstration of LLM-based agents for text classification with dynamic topic discovery.

> 📖 This GUIDE.md explains the concepts, architecture, and how to use this library.
> Each skill has its own README.md in its folder.

---

## Abstract

This project demonstrates a practical approach to text classification using LLMs as reasoning agents. Unlike traditional machine learning classifiers that require fixed labels from the start, this system can discover new categories when patterns emerge in the data. We call this component the "Sentinel" — a monitoring agent that watches for trends and expands the taxonomy dynamically.

**Key contribution:** A hybrid architecture that combines guided classification with autonomous discovery, allowing the system to adapt to real-world data without manual intervention.

---

## 1. Introduction

### 1.1 Problem Statement

Traditional text classifiers face a fundamental limitation: they can only predict labels that existed during training. When new topics emerge in real-world data, these systems either:

1. Force-fit the data into existing categories (wrong)
2. Produce meaningless "other" labels (unhelpful)
3. Require manual retraining (expensive)

### 1.2 Our Approach

We propose an LLM-based agent system with two modes of operation:

| Mode | Function | Trigger |
|------|----------|---------|
| **Guided Classification** | Assign known labels to text | When content matches existing topics |
| **Autonomous Discovery** | Propose new categories | When content does not fit any known topic |

The key insight is that LLMs possess general knowledge that allows them to recognize when something is "different" and suggest what that difference might be called.

---

## 2. System Architecture

### 2.1 Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT TEXT                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │      LLM CLASSIFIER AGENT    │
               │                              │
               │  Task: "Classify this text"  │
               │  Knowledge: Known topics     │
               │  Output: Label + Confidence  │
               └──────────────┬───────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              Matches            No Match
              Known Topic         Found
                    │                   │
                    ▼                   ▼
            ┌─────────────┐    ┌─────────────────────┐
            │  Assign     │    │  Label: UNCATEGORIZED│
            │  Label      │    │  + Suggest new topic │
            └─────────────┘    └──────────┬──────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │    SENTINEL AGENT      │
                              │                        │
                              │  Monitors suggestions  │
                              │  Counts occurrences    │
                              │  Threshold: N hits     │
                              └───────────┬────────────┘
                                          │
                                    N reached?
                                          │
                                    ┌─────┴─────┐
                                   NO          YES
                                    │           │
                                    ▼           ▼
                              ┌─────────┐  ┌────────────────┐
                              │  Wait   │  │ PROMOTE TOPIC  │
                              │  more   │  │ • Add to list  │
                              └─────────┘  │ • Re-tag old   │
                                           │ • Alert user   │
                                           └────────────────┘
```

### 2.2 Components

#### 2.2.1 Classifier Agent

The classifier agent uses an LLM to analyze text and produce structured output:

```python
# Input
review = "The pacing was so slow, I almost fell asleep."

# LLM Prompt
"""
You classify movie reviews.

AVAILABLE TOPICS:
"Acting Performance", "Plot & Story", "Visual Effects", 
"Cinematography", "Soundtrack & Score", "Direction", "Dialogue"

Rules:
1. Match to a known topic if possible
2. If no match, use "UNCATEGORIZED" and suggest a new topic
3. Include sentiment and confidence

Output format (JSON):
{"labels": [...], "sentiment": "...", "confidence": 0.0-1.0, 
 "suggested_label": null or "New Topic"}
"""

# Output
{
  "labels": ["UNCATEGORIZED"],
  "sentiment": "negative",
  "confidence": 0.9,
  "suggested_label": "Pacing Issues",
  "suggestion_reason": "Review discusses tempo/rhythm of the film"
}
```

#### 2.2.2 Sentinel Agent

The Sentinel monitors classification results and tracks topic suggestions:

```python
class Sentinel:
    def __init__(self, threshold=5):
        self.threshold = threshold      # Hits needed to promote
        self.candidates = {}            # Topic -> count + samples
        self.confirmed = []             # Promoted topics

    def observe(self, suggested_topic, review_text):
        """Log a suggestion, promote if threshold reached."""
        
        # Track the suggestion
        if suggested_topic not in self.candidates:
            self.candidates[suggested_topic] = {
                "count": 0,
                "samples": []
            }
        
        self.candidates[suggested_topic]["count"] += 1
        self.candidates[suggested_topic]["samples"].append(review_text)
        
        # Check threshold
        if self.candidates[suggested_topic]["count"] >= self.threshold:
            self._promote(suggested_topic)
            return True
        
        return False
```

#### 2.2.3 LLM Wrapper

A unified interface supporting multiple providers:

```python
def classify(text, topics, provider="ollama"):
    """Classify text using specified LLM provider."""
    
    system_prompt = build_classification_prompt(topics)
    
    response = llm_complete(
        prompt=text,
        system=system_prompt,
        provider=provider,      # ollama, openai, anthropic, google
        temperature=0.1,        # Low = more consistent
        response_format="json"  # Structured output
    )
    
    return parse_classification(response)
```

---

## 3. Why This Works

### 3.1 LLMs as Reasoning Agents

LLMs are trained on vast amounts of text, giving them:

1. **Semantic understanding** — They grasp meaning, not just keywords
2. **General knowledge** — They know what "pacing" means for films
3. **Structured output** — They can produce JSON following instructions
4. **Self-awareness of uncertainty** — They can indicate low confidence

This makes them suitable as reasoning agents that can make judgment calls about text categorization.

### 3.2 The Discovery Mechanism

The key innovation is treating UNCATEGORIZED not as a failure, but as a signal:

| Traditional Approach | Our Approach |
|---------------------|--------------|
| UNCATEGORIZED = error | UNCATEGORIZED = discovery opportunity |
| Requires manual review | Auto-suggests new topic name |
| Fixed taxonomy | Evolving taxonomy |

### 3.3 Threshold-Based Promotion

Using a threshold (e.g., 5 occurrences) before promoting a topic:

- **Prevents noise** — One-off suggestions don't clutter the taxonomy
- **Captures trends** — Recurring patterns get recognized
- **Maintains quality** — Only genuinely useful topics are added

```
Topic: "Pacing Issues"
├─ Hit 1: "The pacing was slow"           [░░░░░] 1/5
├─ Hit 2: "Movie dragged on too long"     [██░░░] 2/5
├─ Hit 3: "Needed tighter editing"        [███░░] 3/5
├─ Hit 4: "Felt rushed in parts"          [████░] 4/5
└─ Hit 5: "Runtime felt longer than 3h"   [█████] 5/5 → PROMOTED!
```

---

## 4. Demonstration

### 4.1 Setup

```bash
# Clone and install
git clone https://github.com/leon5354/llm-agent-demo.git
cd llm-agent-demo
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your LLM provider settings
```

### 4.2 Example Run

**Input Data (reviews.csv):**
```
id,review_text
1,"The acting was phenomenal, truly Oscar-worthy."
2,"CGI looked fake, took me out of the movie."
3,"The pacing was so slow, I almost fell asleep."
4,"Great acting but the plot had holes."
5,"Movie dragged on, needed better pacing."
6,"Acting was wooden and unconvincing."
7,"Felt like a 3-hour film crammed into 90 minutes."
8,"Soundtrack was forgettable."
9,"Another movie ruined by slow pacing."
10,"The tempo was all wrong for an action film."
```

**Execution:**
```bash
python scripts/run.py --input reviews.csv --limit 10
```

**Console Output:**
```
╔════════════════════════════════════════════════════════════════╗
║                    CLASSIFICATION DASHBOARD                     ║
╠════════════════════════════════════════════════════════════════╣
  Processed: 10 reviews
  
  TOPIC DISTRIBUTION:
    Acting Performance   ████ (3)
    Visual Effects       ██ (1)
    Plot & Story         ██ (1)
    Soundtrack           ██ (1)
    UNCATEGORIZED        ████ (4)

  SENTIMENT:
    💚 positive    ███ (3)
    ❤️ negative    ██████ (6)
    🤍 neutral     █ (1)

  PENDING DISCOVERIES:
    Pacing Issues  [████░] 4/5

==================================================
🚨 Sentinel Alert: New category 'Pacing Issues' detected!
   Hits: 5 (threshold reached)
   Samples:
     • "The pacing was so slow, I almost fell asleep."
     • "Movie dragged on, needed better pacing."
     • "Another movie ruined by slow pacing."
==================================================
```

### 4.3 What Happened

1. **Reviews 1, 4, 6** → Classified as "Acting Performance" (known topic)
2. **Review 2** → Classified as "Visual Effects" (known topic)
3. **Reviews 3, 5, 7, 9, 10** → All mentioned pacing → LLM suggested "Pacing Issues"
4. **After 5 hits** → Sentinel promoted "Pacing Issues" to the topic list
5. **Previous UNCATEGORIZED reviews** → Automatically re-tagged

---

## 5. Technical Details

### 5.1 Prompt Engineering

The system prompt is carefully structured:

```
You classify movie reviews.

AVAILABLE TOPICS:
"Acting Performance", "Plot & Story", ...

Rules:
1. First, try to match to AVAILABLE TOPICS
2. If no match, use "UNCATEGORIZED"
3. When UNCATEGORIZED, suggest a new topic name

Output JSON only:
{"labels": [...], "sentiment": "...", "confidence": 0.0-1.0, 
 "suggested_label": null or "New Topic Name"}
```

Key elements:
- **Clear task definition** — "You classify movie reviews"
- **Explicit constraints** — List of available topics
- **Fallback behavior** — What to do when no match
- **Structured output** — JSON format for programmatic use

### 5.2 Temperature Setting

```python
TEMPERATURE = 0.1  # Low for consistency
```

Low temperature (0.0-0.3) makes the model:
- More deterministic
- More consistent across similar inputs
- Less creative (which is good for classification)

### 5.3 Multi-Provider Support

```python
PROVIDERS = {
    "ollama": {
        "url": "http://localhost:11434",
        "models": ["llama3", "mistral", "qwen2"]
    },
    "openai": {
        "models": ["gpt-4o-mini", "gpt-4o"]
    },
    "anthropic": {
        "models": ["claude-3-haiku", "claude-3-sonnet"]
    },
    "google": {
        "models": ["gemini-2.0-flash", "gemini-2.5-pro"]
    }
}
```

---

## 6. Applications

This architecture can be adapted for:

| Domain | Example Topics | Potential Discoveries |
|--------|---------------|----------------------|
| Product reviews | Quality, Price, Shipping | "Packaging", "Instructions" |
| Customer support | Billing, Technical, Account | "App crash", "Login issues" |
| Social media | Politics, Sports, Entertainment | "Meme", "Viral trend" |
| News articles | Politics, Business, Sports | "AI", "Climate" |
| Medical feedback | Symptoms, Treatment, Staff | "Wait time", "Parking" |

---

## 7. Limitations

1. **LLM costs** — Each classification requires an API call
2. **Latency** — Slower than traditional ML classifiers
3. **Hallucination risk** — LLM might suggest inappropriate topics
4. **Threshold tuning** — Requires domain knowledge to set correctly
5. **Provider dependency** — Quality varies by LLM provider

---

## 8. Future Improvements

1. **Batch processing** — Group reviews for efficiency
2. **Confidence filtering** — Only use high-confidence suggestions
3. **Topic merging** — Detect and merge similar discovered topics
4. **Human-in-the-loop** — Require confirmation before promotion
5. **Semantic clustering** — Use embeddings to validate suggestions

---

## 9. Conclusion

This demonstration shows how LLMs can serve as intelligent agents for text classification, going beyond simple label assignment to actively discover new categories. The hybrid approach — combining guided classification with autonomous discovery — provides a practical balance between structure and adaptability.

The key insights are:

1. **LLMs can reason about categories** — Not just pattern match
2. **UNCATEGORIZED is a signal, not an error** — Opportunity for discovery
3. **Thresholds prevent noise** — Only promote genuine trends
4. **Structured output enables automation** — JSON for programmatic use

---

## 10. Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env

# 3. Run with test data
python scripts/run.py --generate --limit 20

# 4. Run with your data
python scripts/run.py --input your_data.csv
```

---

## References

1. Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models.
2. Brown, T., et al. (2020). Language models are few-shot learners.
3. OpenAI (2023). GPT-4 Technical Report.
4. Anthropic (2024). Claude 3 Model Card.

---

## License

MIT License — Free for academic and commercial use.

---

## Citation

```bibtex
@software{llm_agent_demo,
  title = {LLM-Agent Classification with Dynamic Topic Discovery},
  author = {Research Team},
  year = {2026},
  url = {https://github.com/leon5354/llm-agent-demo}
}
```
