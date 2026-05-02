"""SPM unit assignment adapters."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from microunit.core import UnitPartition
from microunit.units._helpers import composite_ids, first_present_column


def assign_spm_partition(
    persons: pd.DataFrame,
    person_col: str = "person_id",
    household_col: str = "household_id",
    family_col: str = "family_id",
    existing_unit_cols: Sequence[str] = (
        "person_spm_unit_id",
        "spm_unit_id",
        "SPM_ID",
    ),
) -> UnitPartition:
    """Assign SPM units, preserving native IDs when present.

    This is a conservative adapter, not yet the full Census-parity constructor.
    If no native SPM unit ID exists, it uses family-within-household when
    available, otherwise household ID.
    """

    existing_col = first_present_column(persons, existing_unit_cols)
    if existing_col is not None:
        return UnitPartition(
            unit_type="spm",
            person_id=persons[person_col],
            unit_id=persons[existing_col],
            source=existing_col,
        )

    if family_col in persons:
        unit_id = composite_ids(persons, household_col, family_col)
        source = f"{household_col}+{family_col}"
    elif household_col in persons:
        unit_id = persons[household_col]
        source = household_col
    else:
        raise KeyError(
            "SPM fallback assignment requires either native SPM IDs, "
            f"{family_col!r}, or {household_col!r}"
        )

    return UnitPartition(
        unit_type="spm",
        person_id=persons[person_col],
        unit_id=unit_id,
        source=source,
    )
