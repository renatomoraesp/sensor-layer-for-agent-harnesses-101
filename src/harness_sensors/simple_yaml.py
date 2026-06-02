"""Small YAML loader for the repository's portable config subset.

The project intentionally keeps runtime dependencies light. If PyYAML is
installed, this module delegates to it. Otherwise it accepts the subset used by
the bundled sensor frontmatter and example configs: mappings, nested mappings,
lists, inline lists, strings, booleans, nulls, and numbers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class _Line:
    indent: int
    text: str


def load_yaml(text: str) -> Any:
    """Load YAML text into Python objects."""

    try:
        import yaml  # type: ignore[import-untyped]
    except ModuleNotFoundError:
        yaml = None

    if yaml is not None:
        return yaml.safe_load(text)

    lines = _prepare_lines(text)
    if not lines:
        return {}
    value, index = _parse_block(lines, 0, lines[0].indent)
    if index != len(lines):
        raise ValueError(f"could not parse YAML line: {lines[index].text}")
    return value


def _prepare_lines(text: str) -> list[_Line]:
    lines: list[_Line] = []
    for raw_line in text.splitlines():
        without_comment = _strip_comment(raw_line.rstrip())
        if not without_comment.strip():
            continue
        indent = len(without_comment) - len(without_comment.lstrip(" "))
        lines.append(_Line(indent=indent, text=without_comment.strip()))
    return lines


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif (
            char == "#"
            and not in_single
            and not in_double
            and (index == 0 or line[index - 1].isspace())
        ):
            return line[:index].rstrip()
    return line


def _parse_block(lines: list[_Line], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    if lines[index].indent < indent:
        return {}, index
    if lines[index].text.startswith("- "):
        return _parse_sequence(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_sequence(lines: list[_Line], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        line = lines[index]
        if line.indent != indent or not line.text.startswith("- "):
            break
        value_text = line.text[2:].strip()
        index += 1
        if not value_text:
            value, index = _parse_block(lines, index, indent + 2)
            items.append(value)
        elif _looks_like_inline_mapping(value_text):
            item = _parse_inline_mapping(value_text)
            if index < len(lines) and lines[index].indent > indent:
                child, index = _parse_block(lines, index, lines[index].indent)
                if isinstance(child, dict):
                    item.update(child)
                else:
                    item["items"] = child
            items.append(item)
        else:
            items.append(_parse_scalar(value_text))
    return items, index


def _parse_mapping(lines: list[_Line], index: int, indent: int) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent != indent or line.text.startswith("- "):
            break
        if ":" not in line.text:
            raise ValueError(f"expected mapping entry, got: {line.text}")
        key, value_text = line.text.split(":", 1)
        key = key.strip()
        value_text = value_text.strip()
        index += 1
        if value_text:
            mapping[key] = _parse_scalar(value_text)
        elif index < len(lines) and lines[index].indent > indent:
            mapping[key], index = _parse_block(lines, index, lines[index].indent)
        else:
            mapping[key] = None
    return mapping, index


def _parse_scalar(value: str) -> Any:
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in _split_inline_list(inner)]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _split_inline_list(value: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    for char in value:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "," and not in_single and not in_double:
            items.append("".join(current))
            current = []
            continue
        current.append(char)
    items.append("".join(current))
    return items


def _looks_like_inline_mapping(value: str) -> bool:
    return ":" in value and not value.startswith(("http://", "https://"))


def _parse_inline_mapping(value: str) -> dict[str, Any]:
    key, raw = value.split(":", 1)
    return {key.strip(): _parse_scalar(raw.strip()) if raw.strip() else {}}
