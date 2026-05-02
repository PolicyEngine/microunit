"""Metadata for known policy-unit schemes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UnitKind = Literal["partition", "ego"]


@dataclass(frozen=True)
class UnitScheme:
    name: str
    kind: UnitKind
    description: str


_SCHEMES: dict[str, UnitScheme] = {
    "spm": UnitScheme(
        name="spm",
        kind="partition",
        description="Supplemental Poverty Measure resource unit.",
    ),
    "tax": UnitScheme(
        name="tax",
        kind="partition",
        description="Federal income tax filing/dependency unit.",
    ),
    "snap": UnitScheme(
        name="snap",
        kind="partition",
        description="SNAP household assignment within a physical household.",
    ),
    "medicaid_magi": UnitScheme(
        name="medicaid_magi",
        kind="ego",
        description="Focal-person Medicaid MAGI household.",
    ),
}


def get_scheme(name: str) -> UnitScheme:
    try:
        return _SCHEMES[name]
    except KeyError as exc:
        known = ", ".join(sorted(_SCHEMES))
        raise KeyError(f"Unknown unit scheme {name!r}. Known schemes: {known}") from exc


def list_schemes() -> tuple[UnitScheme, ...]:
    return tuple(_SCHEMES[name] for name in sorted(_SCHEMES))
