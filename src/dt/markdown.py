from __future__ import annotations

from typing import Optional

import yaml

from dt.constants import REQUIRED_HEADINGS


def _extract_front_matter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        raise ValueError("Missing front matter start")
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("Missing front matter end")
    return parts[0][4:], parts[1]


def _heading_counts(markdown_body: str) -> dict[str, int]:
    counts = {name: 0 for name in REQUIRED_HEADINGS}
    in_fence = False
    for line in markdown_body.splitlines():
        if _is_fence_marker(line):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            heading = line[3:].strip()
            if heading in counts:
                counts[heading] += 1
    return counts


def _parse_headings(markdown_body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: Optional[str] = None
    in_fence = False
    for line in markdown_body.splitlines():
        if _is_fence_marker(line):
            in_fence = not in_fence
            if current is not None:
                sections[current].append(line)
            continue
        if not in_fence and line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _is_fence_marker(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def _write_decision_file(
    decisions_dir,
    payload: dict,
    sections: dict[str, str],
    extra_sections: dict[str, str] | None = None,
):
    from dt.paths import _slugify_title

    slug = _slugify_title(str(payload["title"]))
    out_path = decisions_dir / f"{payload['id']}-{slug}.md"
    yaml_text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip()
    body_lines = ["---", yaml_text, "---", ""]
    for heading in REQUIRED_HEADINGS:
        body_lines.extend([f"## {heading}", sections.get(heading, "TODO"), ""])
    for heading, body in (extra_sections or {}).items():
        body_lines.extend([f"## {heading}", body, ""])
    out_path.write_text("\n".join(body_lines), encoding="utf-8")
    return out_path
