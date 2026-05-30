"""Rules-based helpers for tax-unit construction.

These helpers encode the federal dependency and filing rules used to assign
people into tax units: the qualifying-child age test, the
relationship-to-reference-person tests for qualifying children and qualifying
relatives, and the qualifying-relative gross income limit (the personal- and
dependent-exemption amount under IRC 151(d), used by the IRC 152(d)(1)(B)
gross income test).

The CPS relationship codes mirror the Census ``A_EXPRRP`` recode used in the
ASEC. Consumers that start from a different relationship coding (for example
ACS ``RELSHIPP``) are expected to map onto these codes before calling
:func:`microunit.construct_tax_units`.

The gross income limit is read from package data
(``data/dependent_gross_income_limit.yaml``) so the package is self-contained
and does not depend on ``policyengine-us`` being installed.
"""

from __future__ import annotations

from enum import IntEnum
from functools import cache
from importlib import resources

import yaml


class CPSRelationshipCode(IntEnum):
    """CPS ASEC relationship-to-reference-person recode (``A_EXPRRP``)."""

    REFERENCE_PERSON_WITH_RELATIVES = 1
    REFERENCE_PERSON_WITHOUT_RELATIVES = 2
    HUSBAND = 3
    WIFE = 4
    OWN_CHILD = 5
    GRANDCHILD = 7
    PARENT = 8
    SIBLING = 9
    OTHER_RELATIVE = 10
    FOSTER_CHILD = 11
    NONRELATIVE_WITH_RELATIVES = 12
    PARTNER_OR_ROOMMATE = 13
    NONRELATIVE_WITHOUT_RELATIVES = 14


REFERENCE_PERSON_CODES = frozenset(
    {
        CPSRelationshipCode.REFERENCE_PERSON_WITH_RELATIVES,
        CPSRelationshipCode.REFERENCE_PERSON_WITHOUT_RELATIVES,
    }
)

REFERENCE_SPOUSE_CODES = frozenset(
    {
        CPSRelationshipCode.HUSBAND,
        CPSRelationshipCode.WIFE,
    }
)

REFERENCE_QUALIFYING_CHILD_CODES = frozenset(
    {
        CPSRelationshipCode.OWN_CHILD,
        CPSRelationshipCode.GRANDCHILD,
        CPSRelationshipCode.SIBLING,
        CPSRelationshipCode.FOSTER_CHILD,
    }
)

REFERENCE_QUALIFYING_RELATIVE_CODES = frozenset(
    {
        CPSRelationshipCode.OWN_CHILD,
        CPSRelationshipCode.GRANDCHILD,
        CPSRelationshipCode.PARENT,
        CPSRelationshipCode.SIBLING,
        CPSRelationshipCode.OTHER_RELATIVE,
        CPSRelationshipCode.FOSTER_CHILD,
    }
)


def qualifying_child_age_test(
    age: int | float,
    is_full_time_student: bool = False,
    is_permanently_disabled: bool = False,
    non_student_age_limit: int = 19,
    student_age_limit: int = 24,
) -> bool:
    if is_permanently_disabled:
        return True
    age_limit = student_age_limit if is_full_time_student else non_student_age_limit
    return float(age) < age_limit


def _relationship_from_code(relationship_code: int | None):
    if relationship_code is None:
        return None
    try:
        return CPSRelationshipCode(int(relationship_code))
    except ValueError:
        return None


def reference_relationship_allows_qualifying_child(
    relationship_code: int | None,
) -> bool:
    relationship = _relationship_from_code(relationship_code)
    return relationship in REFERENCE_QUALIFYING_CHILD_CODES


def reference_relationship_allows_qualifying_relative(
    relationship_code: int | None,
) -> bool:
    relationship = _relationship_from_code(relationship_code)
    return relationship in REFERENCE_QUALIFYING_RELATIVE_CODES


def related_to_head_or_spouse(relationship_code: int | None) -> bool:
    relationship = _relationship_from_code(relationship_code)
    return relationship in (
        REFERENCE_PERSON_CODES
        | REFERENCE_SPOUSE_CODES
        | REFERENCE_QUALIFYING_RELATIVE_CODES
    )


@cache
def _gross_income_limit_values() -> dict:
    parameter_path = (
        resources.files("microunit") / "data" / "dependent_gross_income_limit.yaml"
    )
    with parameter_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)["values"]


@cache
def dependent_gross_income_limit(year: int) -> float:
    values = _gross_income_limit_values()

    def _period_year(period) -> int:
        if hasattr(period, "year"):
            return int(period.year)
        return int(str(period)[:4])

    applicable_years = sorted(
        _period_year(period) for period in values if _period_year(period) <= year
    )
    if not applicable_years:
        raise ValueError(f"No dependent gross income limit configured for {year}.")

    selected_year = applicable_years[-1]
    for period, entry in values.items():
        if _period_year(period) == selected_year:
            return float(entry["value"])
    raise ValueError(f"No dependent gross income limit configured for {year}.")
