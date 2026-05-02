"""Adapters that preserve existing source-data unit IDs."""

from __future__ import annotations

import pandas as pd

from microunit.core import UnitPartition


def partition_from_existing_id(
    persons: pd.DataFrame,
    unit_type: str,
    person_col: str = "person_id",
    unit_col: str = "unit_id",
    role_col: str | None = None,
    source: str | None = None,
) -> UnitPartition:
    """Build a partition from an existing person-level unit ID column."""

    return UnitPartition.from_frame(
        persons,
        unit_type=unit_type,
        person_col=person_col,
        unit_col=unit_col,
        role_col=role_col,
        source=source or unit_col,
    )
