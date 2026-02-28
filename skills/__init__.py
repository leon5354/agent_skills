"""
LLM-Agent Skills Library

A collection of reusable agent skills for LLM-based applications.

Available Skills:
    - classifier: Text classification with topic discovery
    - sentinel: Dynamic topic discovery agent
    - llm-wrapper: Multi-provider LLM interface
"""

from skills.classifier.skill import ClassifierSkill, Result
from skills.sentinel.skill import SentinelSkill
from skills.llm_wrapper.skill import complete, provider_info

__all__ = [
    "ClassifierSkill",
    "Result",
    "SentinelSkill",
    "complete",
    "provider_info",
]
