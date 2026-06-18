from __future__ import annotations

import hashlib
import re

from dt.constants import REF_PATTERNS
from dt.models import ValidationMessage


SUPPORTED_BACKFILL_EVIDENCE = (
    "git:commit:<7-40 hex>",
    "path:",
    "url:https://",
    "github:issue:",
    "github:pr:",
    "dvc:",
    "data:version:",
    "checksum:sha256:",
    "mlflow:run:",
    "wandb:run:",
    "run:",
)
GIT_COMMIT_EVIDENCE_RE = re.compile(r"^git:commit:[0-9a-fA-F]{7,40}$")


def _ref_is_valid(ref) -> bool:
    if not isinstance(ref, str) or not ref.strip():
        return False
    return any(pattern.match(ref) for pattern in REF_PATTERNS)


def _infer_target_id(ref: str) -> str:
    if ref.startswith("decision:"):
        return ref
    digest = hashlib.sha256(ref.encode("utf-8")).hexdigest()
    return f"artifact:{digest}"


def _evidence_link_for_ref(ref: str, index: int) -> dict[str, str]:
    if ref.startswith("git:commit:"):
        rel = "implements"
        artifact_kind = "code"
    elif ref.startswith(("path:", "url:https://")):
        rel = "supported_by"
        artifact_kind = "document"
    elif ref.startswith("github:issue:"):
        rel = "supported_by"
        artifact_kind = "issue"
    elif ref.startswith("github:pr:"):
        rel = "implements"
        artifact_kind = "code"
    elif ref.startswith(("dvc:", "data:version:", "checksum:sha256:")):
        rel = "supported_by"
        artifact_kind = "data"
    elif ref.startswith(("mlflow:run:", "wandb:run:", "run:")):
        rel = "evaluated_by"
        artifact_kind = "experiment_run"
    else:
        raise ValueError(
            "unsupported evidence ref for backfill link mapping: "
            f"{ref}. Supported prefixes: {', '.join(SUPPORTED_BACKFILL_EVIDENCE)}"
        )
    return {
        "id": f"L-{index:04d}",
        "rel": rel,
        "artifact_kind": artifact_kind,
        "ref": ref,
        "label": f"Backfill evidence {index}",
        "note": "Historical reconstruction evidence",
    }


def _validate_evidence_refs(refs: list[str]) -> list[ValidationMessage]:
    errors: list[ValidationMessage] = []
    for index, ref in enumerate(refs, start=1):
        if not _ref_is_valid(ref):
            errors.append(ValidationMessage("LINK_INVALID_FORMAT", f"evidence_refs[{index}] is not a valid ref"))
            continue
        if ref.startswith("git:commit:") and not GIT_COMMIT_EVIDENCE_RE.match(ref):
            errors.append(
                ValidationMessage(
                    "LINK_INVALID_FORMAT",
                    f"evidence_refs[{index}] git commit evidence must be git:commit:<7-40 hex chars>",
                )
            )
            continue
        try:
            _evidence_link_for_ref(ref, index)
        except ValueError as exc:
            errors.append(ValidationMessage("LINK_INVALID_FORMAT", str(exc)))
    return errors
