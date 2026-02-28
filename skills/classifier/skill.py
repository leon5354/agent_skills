"""
Classifier Skill - Text classification using LLM reasoning.

Purpose:
    Classifies text into known topics using an LLM agent.
    When no topic matches, suggests new category names.

Usage:
    from skills.classifier.skill import ClassifierSkill
    
    classifier = ClassifierSkill(topics=["Topic A", "Topic B"])
    result = classifier.classify("Some text to classify")
    print(result.labels, result.sentiment)
"""

import json
import re
import logging
from typing import Optional, List
from pydantic import BaseModel, field_validator

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import MASTER_TOPICS, MIN_CONFIDENCE
from skills.llm_wrapper.skill import complete

logger = logging.getLogger(__name__)


class Result(BaseModel):
    """Classification output structure."""
    labels: List[str]
    sentiment: str
    confidence: float = 0.8
    suggested_label: Optional[str] = None
    suggestion_reason: Optional[str] = None

    @field_validator("labels")
    @classmethod
    def clean_labels(cls, v):
        return [label.strip() for label in v if label.strip()]

    @field_validator("sentiment")
    @classmethod
    def normalize_sentiment(cls, v):
        valid = ["positive", "negative", "neutral", "mixed"]
        normalized = v.lower().strip()
        return normalized if normalized in valid else "neutral"


def _build_prompt(known_topics: List[str]) -> str:
    """Build the classification prompt with current topics."""
    topics_str = ", ".join(f'"{t}"' for t in known_topics)

    return f"""You are a text classification agent.

AVAILABLE TOPICS:
{topics_str}

Your task:
1. Read the input text
2. Determine which topic(s) it discusses
3. If it matches a known topic, use that label
4. If it does NOT match any known topic, use "UNCATEGORIZED"
5. When UNCATEGORIZED, suggest a new topic name

Sentiment options: positive, negative, neutral, mixed

Output JSON format:
{{"labels": ["Topic Name"], "sentiment": "neutral", "confidence": 0.9, "suggested_label": null}}

For uncategorized:
{{"labels": ["UNCATEGORIZED"], "sentiment": "negative", "confidence": 0.85, "suggested_label": "New Topic", "suggestion_reason": "Why this is new"}}"""


def _parse_json(text: str) -> dict:
    """Extract JSON from LLM output."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}


class ClassifierSkill:
    """
    LLM-based text classifier.
    
    Assigns topics to text and suggests new categories when needed.
    """

    def __init__(self, topics: List[str] = None):
        """
        Initialize classifier with topic list.
        
        Args:
            topics: List of known topic names
        """
        self.topics = topics or MASTER_TOPICS.copy()

    def add_topic(self, topic: str) -> bool:
        """Add a new topic to the active list."""
        clean = topic.strip().title()
        if clean and clean not in self.topics:
            self.topics.append(clean)
            logger.info(f"Added topic: {clean}")
            return True
        return False

    def classify(self, text: str) -> Result:
        """
        Classify a single text input.
        
        Args:
            text: The text to classify
            
        Returns:
            Result with labels, sentiment, confidence
        """
        system = _build_prompt(self.topics)
        user = f'Classify:\n\n"{text}"'

        try:
            raw = complete(prompt=user, system=system, json_mode=True)
            data = _parse_json(raw)

            # Match labels to known topics
            final_labels = []
            for label in data.get("labels", []):
                clean = label.strip()
                if clean.upper() == "UNCATEGORIZED":
                    final_labels.append("UNCATEGORIZED")
                else:
                    matched = False
                    for known in self.topics:
                        if clean.lower() in known.lower() or known.lower() in clean.lower():
                            final_labels.append(known)
                            matched = True
                            break
                    if not matched:
                        final_labels.append(clean)

            return Result(
                labels=final_labels,
                sentiment=data.get("sentiment", "neutral"),
                confidence=data.get("confidence", 0.7),
                suggested_label=data.get("suggested_label"),
                suggestion_reason=data.get("suggestion_reason"),
            )

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return Result(labels=[], sentiment="neutral", confidence=0.0)

    def get_topics(self) -> List[str]:
        """Return current topic list."""
        return self.topics.copy()
