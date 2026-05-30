"""Microdata unit assignment primitives."""

from microunit.core import EgoUnitMembership, UnitPartition
from microunit.diagnostics import PartitionMatchReport, partition_match_report
from microunit.registry import UnitKind, UnitScheme, get_scheme, list_schemes
from microunit.rule_helpers import (
    REFERENCE_PERSON_CODES,
    REFERENCE_QUALIFYING_CHILD_CODES,
    REFERENCE_QUALIFYING_RELATIVE_CODES,
    REFERENCE_SPOUSE_CODES,
    CPSRelationshipCode,
    dependent_gross_income_limit,
    qualifying_child_age_test,
    reference_relationship_allows_qualifying_child,
    reference_relationship_allows_qualifying_relative,
    related_to_head_or_spouse,
)
from microunit.tax_unit_construction import (
    CENSUS_DOCUMENTED_MODE,
    DEPENDENT,
    HEAD,
    POLICYENGINE_MODE,
    SPOUSE,
    SUPPORTED_TAX_UNIT_CONSTRUCTION_MODES,
    construct_tax_units,
    estimate_dependent_gross_income,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # Core containers
    "EgoUnitMembership",
    "PartitionMatchReport",
    "UnitKind",
    "UnitPartition",
    "UnitScheme",
    "get_scheme",
    "list_schemes",
    "partition_match_report",
    # Rules-based tax-unit construction engine
    "construct_tax_units",
    "estimate_dependent_gross_income",
    "HEAD",
    "SPOUSE",
    "DEPENDENT",
    "POLICYENGINE_MODE",
    "CENSUS_DOCUMENTED_MODE",
    "SUPPORTED_TAX_UNIT_CONSTRUCTION_MODES",
    "CPSRelationshipCode",
    "REFERENCE_PERSON_CODES",
    "REFERENCE_SPOUSE_CODES",
    "REFERENCE_QUALIFYING_CHILD_CODES",
    "REFERENCE_QUALIFYING_RELATIVE_CODES",
    "dependent_gross_income_limit",
    "qualifying_child_age_test",
    "reference_relationship_allows_qualifying_child",
    "reference_relationship_allows_qualifying_relative",
    "related_to_head_or_spouse",
]
