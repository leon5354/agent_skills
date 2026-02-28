#!/usr/bin/env python3
"""
Main entry point for LLM-Agent Demo.
"""

import argparse
import csv
import logging
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    MASTER_TOPICS, DISCOVERY_THRESHOLD,
    INPUT_FILE_PATH, OUTPUT_FILE_PATH,
    COMMENT_COL_NAME
)
from skills.classifier.skill import ClassifierSkill
from skills.sentinel.skill import SentinelSkill
from skills.llm_wrapper.skill import provider_info

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def generate_test_data(n: int = 20) -> list[dict]:
    """Generate synthetic reviews for testing."""
    reviews = [
        ("The acting was phenomenal, truly Oscar-worthy.", "Acting"),
        ("CGI looked fake and took me out of the movie.", "Visual Effects"),
        ("The pacing was so slow, I almost fell asleep.", "Pacing Issues"),
        ("Great acting but the plot had holes.", "Acting"),
        ("Movie dragged on, needed tighter editing.", "Pacing Issues"),
        ("Cinematography was stunning.", "Cinematography"),
        ("The dialogue felt unnatural and forced.", "Dialogue"),
        ("Soundtrack was forgettable.", "Soundtrack"),
        ("Director's vision really shone through.", "Direction"),
        ("The tempo was all wrong for an action film.", "Pacing Issues"),
        ("Lead actor carried the entire movie.", "Acting"),
        ("Visual effects were groundbreaking.", "Visual Effects"),
        ("Story was predictable and boring.", "Plot"),
        ("Another movie ruined by slow pacing.", "Pacing Issues"),
        ("Acting was wooden and unconvincing.", "Acting"),
        ("The film's rhythm was perfectly balanced.", "Pacing Issues"),
        ("Explosions looked cheap.", "Visual Effects"),
        ("Plot twists were genuinely surprising.", "Plot"),
        ("Felt rushed, too much crammed in.", "Pacing Issues"),
        ("Supporting cast stole every scene.", "Acting"),
    ]
    return [{"id": i, "review_text": r[0]} for i, r in enumerate(reviews[:n])]


def print_dashboard(results, classifier, sentinel):
    """Print summary dashboard."""
    total = len(results)
    all_labels, sentiments = [], []
    
    for r in results:
        all_labels.extend(r.get("labels", []))
        sentiments.append(r.get("sentiment", "neutral"))
    
    topic_counts = Counter(all_labels)
    sent_counts = Counter(sentiments)
    
    lines = [
        "",
        "╔" + "═" * 60 + "╗",
        "║" + "CLASSIFICATION DASHBOARD".center(60) + "║",
        "╠" + "═" * 60 + "╣",
        f"  Processed: {total}",
        "",
        "  TOPICS:",
    ]
    
    for topic, count in topic_counts.most_common(10):
        bar = "█" * min(count, 20)
        lines.append(f"    {topic:<24} {bar} ({count})")
    
    lines.append("")
    lines.append("  SENTIMENT:")
    emojis = {"positive": "💚", "negative": "❤️", "neutral": "🤍", "mixed": "💛"}
    for sent, count in sent_counts.most_common():
        bar = "█" * min(count, 20)
        lines.append(f"    {emojis.get(sent, '⚪')} {sent:<10} {bar} ({count})")
    
    pending = sentinel.get_pending()
    if pending:
        lines.append("")
        lines.append("  PENDING DISCOVERIES:")
        for topic, count in sorted(pending.items(), key=lambda x: -x[1]):
            bar = "█" * count + "░" * (sentinel.threshold - count)
            lines.append(f"    • {topic} [{bar}] {count}/{sentinel.threshold}")
    
    lines.append("╚" + "═" * 60 + "╝")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="LLM-Agent Demo")
    parser.add_argument("--input", "-i", default=INPUT_FILE_PATH)
    parser.add_argument("--review-col", "-c", default=COMMENT_COL_NAME)
    parser.add_argument("--generate", "-g", action="store_true")
    parser.add_argument("--limit", "-l", type=int)
    parser.add_argument("--output", "-o", default=OUTPUT_FILE_PATH)
    args = parser.parse_args()

    info = provider_info()
    print(f"\n🤖 Provider: {info['provider']} / {info['model']}")

    if args.generate:
        print("📝 Generating test data...")
        rows = generate_test_data(args.limit or 20)
    else:
        print(f"📂 Loading: {args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    if args.limit:
        rows = rows[:args.limit]
    print(f"   {len(rows)} rows\n")

    classifier = ClassifierSkill(topics=MASTER_TOPICS.copy())
    sentinel = SentinelSkill(threshold=DISCOVERY_THRESHOLD)

    results = []
    for i, row in enumerate(rows):
        text = row.get(args.review_col, "")
        if not text:
            continue

        result = classifier.classify(text)

        if result.suggested_label and "UNCATEGORIZED" in result.labels:
            if sentinel.observe(result.suggested_label, text, idx=i):
                classifier.add_topic(result.suggested_label)

        row_data = dict(row)
        row_data["labels"] = result.labels
        row_data["sentiment"] = result.sentiment
        row_data["confidence"] = result.confidence
        results.append(row_data)

        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{len(rows)}...")

    print_dashboard(results, classifier, sentinel)
    print(sentinel.status())

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"\n✅ Saved: {args.output}")
    
    if sentinel.get_confirmed():
        print(f"🎉 Discovered: {', '.join(sentinel.get_confirmed())}")


if __name__ == "__main__":
    main()
