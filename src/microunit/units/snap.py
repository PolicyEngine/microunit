"""SNAP unit assignment adapters."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from microunit.core import UnitPartition
from microunit.units._helpers import first_present_column
from microunit.units.programs import assign_program_partition_from_spm


def assign_snap_partition(
    persons: pd.DataFrame,
    person_col: str = "person_id",
    household_col: str = "household_id",
    family_col: str = "family_id",
    existing_unit_cols: Sequence[str] = (
        "person_snap_unit_id",
        "snap_unit_id",
        "SNAP_UNIT_ID",
    ),
    use_spm_simplification: bool = True,
) -> UnitPartition:
    """Assign SNAP units, preserving existing IDs when present.

    SNAP units often differ from SPM units. Until full SNAP rules are ported,
    the default fallback approximates SNAP households with SPM units.
    """

    unit_col = first_present_column(persons, existing_unit_cols)
    if unit_col is not None:
        return UnitPartition(
            unit_type="snap",
            person_id=persons[person_col],
            unit_id=persons[unit_col],
            source=unit_col,
        )

    if use_spm_simplification:
        return assign_program_partition_from_spm(
            persons,
            program="snap",
            person_col=person_col,
            household_col=household_col,
            family_col=family_col,
        )

    raise KeyError(
        "No SNAP unit ID column found. Pass use_spm_simplification=True "
        "to approximate SNAP units with SPM units."
    )
