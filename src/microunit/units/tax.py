"""Tax unit assignment adapters."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from microunit.core import UnitPartition
from microunit.tax_unit_construction import POLICYENGINE_MODE, construct_tax_units
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

    If no source tax-unit ID is present, callers should instead run the
    rules-based constructor via :func:`construct_tax_partition`, which applies
    federal filing/dependency rules to CPS-like person records. This adapter
    intentionally fails rather than inventing filing units when no source
    assignment is available.
    """

    unit_col = first_present_column(persons, existing_unit_cols)
    if unit_col is None:
        raise KeyError(
            "No tax-unit ID column found. Expected one of: "
            + ", ".join(existing_unit_cols)
            + ". To construct tax units from CPS-like records, use "
            "construct_tax_partition()."
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


def construct_tax_partition(
    persons: pd.DataFrame,
    year: int,
    mode: str = POLICYENGINE_MODE,
    person_col: str = "person_id",
) -> UnitPartition:
    """Construct tax units from CPS-like person records using filing rules.

    This is a thin :class:`~microunit.core.UnitPartition` adapter over
    :func:`microunit.construct_tax_units`. ``persons`` must use the CPS-like
    column contract documented on ``construct_tax_units`` (``PH_SEQ``,
    ``A_LINENO``, ``A_AGE``, ``A_MARITL``, ``A_SPOUSE``, ``PEPAR1``,
    ``PEPAR2``, ``A_EXPRRP``, plus optional income/enrollment/disability
    columns). Consumers reading non-CPS sources (e.g. ACS PUMS) must map their
    columns onto this contract first.

    The returned partition's ``unit_id`` is the dense ``TAX_ID`` and its
    ``role`` carries the decoded ``HEAD``/``SPOUSE``/``DEPENDENT`` role.
    """

    assignments, _ = construct_tax_units(persons, year=year, mode=mode)
    roles = assignments["tax_unit_role_input"].map(
        lambda value: value.decode() if isinstance(value, bytes) else value
    )
    person_id = (
        persons[person_col]
        if person_col in persons
        else pd.Series(range(len(persons)), name=person_col)
    )
    return UnitPartition(
        unit_type="tax",
        person_id=person_id.reset_index(drop=True),
        unit_id=assignments["TAX_ID"].reset_index(drop=True),
        role=roles.reset_index(drop=True),
        source=f"construct_tax_units:{mode}",
    )
