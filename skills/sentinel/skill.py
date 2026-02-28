"""
Sentinel Skill - Dynamic topic discovery.

Purpose:
    Monitors classification results for new topic opportunities.
    When a suggested topic reaches threshold, it gets promoted.

Usage:
    from skills.sentinel.skill import SentinelSkill
    
    sentinel = SentinelSkill(threshold=5)
    promoted = sentinel.observe("New Topic", "Some text", idx=0)
    if promoted:
        print(f"Topic promoted: {sentinel.get_confirmed()}")
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import DISCOVERY_THRESHOLD, SENTINEL_LOG_FILE

logger = logging.getLogger(__name__)


class Alert(BaseModel):
    """Record of a topic promotion event."""
    topic: str
    hits: int
    first_seen: str
    promoted_at: str
    samples: List[str] = []


class SentinelSkill:
    """
    Topic discovery agent.
    
    Watches for patterns and auto-promotes new topics when threshold reached.
    """

    def __init__(self, threshold: int = DISCOVERY_THRESHOLD):
        """
        Initialize sentinel.
        
        Args:
            threshold: Number of hits needed to promote a topic
        """
        self.threshold = threshold
        self.candidates: Dict[str, dict] = {}
        self.confirmed: List[str] = []
        self.log_path = Path(SENTINEL_LOG_FILE)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def observe(
        self,
        suggested_topic: str,
        text: str,
        idx: int = None
    ) -> bool:
        """
        Log a topic suggestion.
        
        Args:
            suggested_topic: Name of the suggested new topic
            text: The text that triggered the suggestion
            idx: Optional row index for re-tagging
            
        Returns:
            True if topic was promoted (threshold reached)
        """
        if not suggested_topic:
            return False

        key = suggested_topic.strip().title()

        if key in self.confirmed:
            return False

        if key not in self.candidates:
            self.candidates[key] = {
                "count": 0,
                "first_seen": datetime.now().isoformat(),
                "samples": [],
                "indices": [],
            }

        self.candidates[key]["count"] += 1
        if idx is not None:
            self.candidates[key]["indices"].append(idx)

        if len(self.candidates[key]["samples"]) < 5:
            self.candidates[key]["samples"].append(text[:200])

        if self.candidates[key]["count"] >= self.threshold:
            self._promote(key)
            return True

        return False

    def _promote(self, topic: str) -> None:
        """Promote candidate to confirmed status."""
        self.confirmed.append(topic)
        data = self.candidates[topic]

        logger.info(
            f"\n{'='*50}\n"
            f"🚨 Sentinel: New topic '{topic}' discovered!\n"
            f"   Hits: {data['count']}\n"
            f"{'='*50}"
        )

        self._log_alert(Alert(
            topic=topic,
            hits=data["count"],
            first_seen=data["first_seen"],
            promoted_at=datetime.now().isoformat(),
            samples=data["samples"],
        ))

    def _log_alert(self, alert: Alert) -> None:
        """Append alert to JSON log."""
        entries = []
        if self.log_path.exists():
            try:
                with open(self.log_path, "r") as f:
                    entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        entries.append(alert.model_dump())
        with open(self.log_path, "w") as f:
            json.dump(entries, f, indent=2, default=str)

    def get_indices(self, topic: str) -> List[int]:
        """Get row indices for a topic (for re-tagging)."""
        key = topic.strip().title()
        if key in self.candidates:
            return self.candidates[key].get("indices", [])
        return []

    def get_pending(self) -> Dict[str, int]:
        """Topics waiting to reach threshold."""
        return {
            t: d["count"]
            for t, d in self.candidates.items()
            if t not in self.confirmed
        }

    def get_confirmed(self) -> List[str]:
        """Topics that have been promoted."""
        return self.confirmed.copy()

    def status(self) -> str:
        """Human-readable status."""
        lines = [
            "🔍 Sentinel Status",
            "-" * 30,
            f"Threshold: {self.threshold}",
            f"Watching: {len(self.candidates)} candidates",
            f"Promoted: {len(self.confirmed)} topics",
        ]

        if self.confirmed:
            lines.append("\n✅ Promoted:")
            for t in self.confirmed:
                lines.append(f"   • {t}")

        pending = self.get_pending()
        if pending:
            lines.append("\n⏳ Pending:")
            for t, count in sorted(pending.items(), key=lambda x: -x[1]):
                bar = "█" * count + "░" * (self.threshold - count)
                lines.append(f"   • {t} [{bar}] {count}/{self.threshold}")

        return "\n".join(lines)
