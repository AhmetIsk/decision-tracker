from __future__ import annotations

import hashlib

from dt.constants import REF_PATTERNS
from dt.models import ValidationMessage


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
    elif ref.startswith("path:"):
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
        raise ValueError(f"unsupported evidence ref for backfill link mapping: {ref}")
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
        try:
            _evidence_link_for_ref(ref, index)
        except ValueError as exc:
            errors.append(ValidationMessage("LINK_INVALID_FORMAT", str(exc)))
    return errors
