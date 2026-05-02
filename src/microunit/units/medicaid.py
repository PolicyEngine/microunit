"""Medicaid MAGI unit adapters."""

from __future__ import annotations

import pandas as pd

from microunit.core import EgoUnitMembership
from microunit.units.programs import assign_ego_units_from_spm


def medicaid_magi_from_membership_frame(
    memberships: pd.DataFrame,
    focal_person_col: str = "focal_person_id",
    member_person_col: str = "member_person_id",
    role_col: str | None = None,
    source: str | None = None,
) -> EgoUnitMembership:
    """Build focal-person Medicaid MAGI units from membership rows."""

    role = memberships[role_col] if role_col is not None else None
    return EgoUnitMembership(
        unit_type="medicaid_magi",
        focal_person_id=memberships[focal_person_col],
        member_person_id=memberships[member_person_col],
        role=role,
        source=source,
    )


def medicaid_magi_from_spm(
    persons: pd.DataFrame,
    person_col: str = "person_id",
    household_col: str = "household_id",
    family_col: str = "family_id",
) -> EgoUnitMembership:
    """Approximate each focal person's MAGI household with their SPM unit."""

    return assign_ego_units_from_spm(
        persons,
        program="medicaid_magi",
        person_col=person_col,
        household_col=household_col,
        family_col=family_col,
    )
