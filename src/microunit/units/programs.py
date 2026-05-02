"""Temporary program-unit simplifications."""

from __future__ import annotations

import pandas as pd

from microunit.core import EgoUnitMembership, UnitPartition
from microunit.units.spm import assign_spm_partition


def assign_program_partition_from_spm(
    persons: pd.DataFrame,
    program: str,
    person_col: str = "person_id",
    household_col: str = "household_id",
    family_col: str = "family_id",
) -> UnitPartition:
    """Approximate a partition-style program unit with SPM units."""

    spm = assign_spm_partition(
        persons,
        person_col=person_col,
        household_col=household_col,
        family_col=family_col,
    )
    return UnitPartition(
        unit_type=program,
        person_id=spm.person_id,
        unit_id=spm.unit_id,
        source=f"spm_simplification:{spm.source}",
    )


def assign_ego_units_from_spm(
    persons: pd.DataFrame,
    program: str,
    person_col: str = "person_id",
    household_col: str = "household_id",
    family_col: str = "family_id",
) -> EgoUnitMembership:
    """Approximate focal-person program units with each person's SPM unit."""

    spm = assign_spm_partition(
        persons,
        person_col=person_col,
        household_col=household_col,
        family_col=family_col,
    )
    frame = spm.to_frame()
    rows = frame.merge(frame, on="unit_id", suffixes=("_focal", "_member"))
    return EgoUnitMembership(
        unit_type=program,
        focal_person_id=rows["person_id_focal"],
        member_person_id=rows["person_id_member"],
        source=f"spm_simplification:{spm.source}",
    )
