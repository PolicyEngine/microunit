"""Tax unit assignment adapters."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from microunit.core import UnitPartition
from microunit.units._helpers import first_present_column


def assign_tax_partition(
    persons: pd.DataFrame,
    person_col: str = "person_id",
    existing_unit_cols: Sequence[str] = (
        "person_tax_unit_id",
        "tax_unit_id",
        "TAX_ID",
    ),
    role_cols: Sequence[str] = ("tax_unit_role_input", "tax_unit_role"),
) -> UnitPartition:
    """Assign tax units by preserving an existing source-data tax-unit ID.

    Full rules-based tax-unit construction should be ported here from the
    current PolicyEngine prototype. This adapter intentionally fails rather
    than inventing filing units when no source assignment is available.
    """

    unit_col = first_present_column(persons, existing_unit_cols)
    if unit_col is None:
        raise KeyError(
            "No tax-unit ID column found. Expected one of: "
            + ", ".join(existing_unit_cols)
        )

    role_col = first_present_column(persons, role_cols)
    role = persons[role_col] if role_col is not None else None
    return UnitPartition(
        unit_type="tax",
        person_id=persons[person_col],
        unit_id=persons[unit_col],
        role=role,
        source=unit_col,
    )
