from __future__ import annotations

from typing import Any

from dt.models import ValidationMessage
from dt.refs import _ref_is_valid
from dt.utils import _is_non_empty_mapping, _is_non_empty_string


def _template_payload(decision_type: str) -> dict[str, Any]:
    if decision_type == "model":
        return {
            "model_spec": {
                "objective": "TODO",
                "model_family": "TODO",
                "input": "TODO",
                "output": "TODO",
                "primary_metric": "TODO",
                "acceptance_criteria": "TODO",
            }
        }
    if decision_type == "evaluation_protocol":
        return {
            "eval_spec": {
                "dataset_ref": "data:version:TODO",
                "protocol": "TODO",
                "metrics": [{"name": "TODO", "threshold": "TODO"}],
                "baseline": {
                    "ref": "run:TODO",
                    "description": "TODO",
                },
            }
        }
    return {}


def _template_validation_errors(doc: dict[str, Any]) -> list[ValidationMessage]:
    errors: list[ValidationMessage] = []
    decision_type = doc.get("type")

    if decision_type == "model":
        spec = doc.get("model_spec")
        if not isinstance(spec, dict):
            errors.append(ValidationMessage("TEMPLATE_FIELD_MISSING", "Missing object: model_spec"))
            return errors
        for field_name in (
            "objective",
            "model_family",
            "input",
            "output",
            "primary_metric",
            "acceptance_criteria",
        ):
            if not _is_non_empty_string(spec.get(field_name)):
                errors.append(
                    ValidationMessage(
                        "TEMPLATE_FIELD_MISSING",
                        f"model_spec.{field_name} must be a non-empty string",
                    )
                )
        training_config = spec.get("training_config")
        if training_config is not None:
            if not isinstance(training_config, dict):
                errors.append(
                    ValidationMessage(
                        "TEMPLATE_FIELD_MISSING",
                        "model_spec.training_config must be an object when present",
                    )
                )
            else:
                for field_name in ("tuning_method", "selection_rule"):
                    if not _is_non_empty_string(training_config.get(field_name)):
                        errors.append(
                            ValidationMessage(
                                "TEMPLATE_FIELD_MISSING",
                                f"model_spec.training_config.{field_name} must be a non-empty string",
                            )
                        )
                if not _is_non_empty_mapping(training_config.get("selected_hyperparameters")):
                    errors.append(
                        ValidationMessage(
                            "TEMPLATE_FIELD_MISSING",
                            "model_spec.training_config.selected_hyperparameters must be a non-empty object",
                        )
                    )
                for field_name in ("stopping_rule", "compute_environment"):
                    value = training_config.get(field_name)
                    if value is not None and not _is_non_empty_string(value):
                        errors.append(
                            ValidationMessage(
                                "TEMPLATE_FIELD_MISSING",
                                f"model_spec.training_config.{field_name} must be a non-empty string when present",
                            )
                        )
                search_space = training_config.get("search_space")
                if search_space is not None and not _is_non_empty_mapping(search_space):
                    errors.append(
                        ValidationMessage(
                            "TEMPLATE_FIELD_MISSING",
                            "model_spec.training_config.search_space must be a non-empty object when present",
                        )
                    )

    if decision_type == "evaluation_protocol":
        spec = doc.get("eval_spec")
        if not isinstance(spec, dict):
            errors.append(ValidationMessage("TEMPLATE_FIELD_MISSING", "Missing object: eval_spec"))
            return errors

        dataset_ref = spec.get("dataset_ref")
        if not _is_non_empty_string(dataset_ref):
            errors.append(
                ValidationMessage("TEMPLATE_FIELD_MISSING", "eval_spec.dataset_ref must be a non-empty string")
            )
        elif not _ref_is_valid(dataset_ref):
            errors.append(ValidationMessage("LINK_INVALID_FORMAT", "eval_spec.dataset_ref must be a valid ref"))

        if not _is_non_empty_string(spec.get("protocol")):
            errors.append(ValidationMessage("TEMPLATE_FIELD_MISSING", "eval_spec.protocol must be a non-empty string"))

        metrics = spec.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            errors.append(
                ValidationMessage("TEMPLATE_FIELD_MISSING", "eval_spec.metrics must be a non-empty list")
            )
        else:
            for index, metric in enumerate(metrics, start=1):
                if not isinstance(metric, dict):
                    errors.append(
                        ValidationMessage(
                            "TEMPLATE_FIELD_MISSING",
                            f"eval_spec.metrics[{index}] must be an object",
                        )
                    )
                    continue
                if not _is_non_empty_string(metric.get("name")):
                    errors.append(
                        ValidationMessage(
                            "TEMPLATE_FIELD_MISSING",
                            f"eval_spec.metrics[{index}].name must be a non-empty string",
                        )
                    )
                if not _is_non_empty_string(metric.get("threshold")):
                    errors.append(
                        ValidationMessage(
                            "TEMPLATE_FIELD_MISSING",
                            f"eval_spec.metrics[{index}].threshold must be a non-empty string",
                        )
                    )

        baseline = spec.get("baseline")
        if not isinstance(baseline, dict):
            errors.append(ValidationMessage("TEMPLATE_FIELD_MISSING", "eval_spec.baseline must be an object"))
        else:
            baseline_ref = baseline.get("ref")
            if not _is_non_empty_string(baseline_ref):
                errors.append(
                    ValidationMessage(
                        "TEMPLATE_FIELD_MISSING",
                        "eval_spec.baseline.ref must be a non-empty string",
                    )
                )
            elif not _ref_is_valid(baseline_ref):
                errors.append(ValidationMessage("LINK_INVALID_FORMAT", "eval_spec.baseline.ref must be a valid ref"))
            if not _is_non_empty_string(baseline.get("description")):
                errors.append(
                    ValidationMessage(
                        "TEMPLATE_FIELD_MISSING",
                        "eval_spec.baseline.description must be a non-empty string",
                    )
                )

    return errors
