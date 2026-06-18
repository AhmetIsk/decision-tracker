from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ValidationMessage:
    code: str
    message: str


@dataclass
class ScaffoldChanges:
    created: list[str] = field(default_factory=list)
    replaced: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


@dataclass
class LoadedRecord:
    path: Path
    yaml_id: str
    doc: Optional[dict[str, Any]] = None
    headings: dict[str, str] = field(default_factory=dict)
    heading_counts: dict[str, int] = field(default_factory=dict)
    parse_errors: list[ValidationMessage] = field(default_factory=list)


@dataclass
class DecisionComputed:
    raw: dict[str, Any]
    links_sorted: list[dict[str, Any]]
    headings: dict[str, str]
    stakeholders: list[str]
    has_minimum_trace_links: int
    score_completeness: float
    score_connectedness: float
    score_inclusiveness: float
    score_traceability: float
    rel_counts: dict[str, int]
    unique_artifacts_by_kind: dict[str, int]
    unique_artifacts_total: int
    unique_decision_targets_total: int
    alternatives_is_na: int


@dataclass
class ValidationContext:
    incoming_supersedes: dict[str, int]
    all_ids: set[str]
    duplicate_ids: set[str]


@dataclass
class DiscoverCandidate:
    sha: str
    title: str
    stage: str
    decision_type: str
