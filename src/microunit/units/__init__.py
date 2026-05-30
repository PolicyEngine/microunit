"""Unit assignment adapters."""

from microunit.units.medicaid import (
    medicaid_magi_from_membership_frame,
    medicaid_magi_from_spm,
)
from microunit.units.passthrough import partition_from_existing_id
from microunit.units.programs import (
    assign_ego_units_from_spm,
    assign_program_partition_from_spm,
)
from microunit.units.snap import assign_snap_partition
from microunit.units.spm import assign_spm_partition
from microunit.units.tax import assign_tax_partition, construct_tax_partition

__all__ = [
    "assign_ego_units_from_spm",
    "assign_program_partition_from_spm",
    "assign_snap_partition",
    "assign_spm_partition",
    "assign_tax_partition",
    "construct_tax_partition",
    "medicaid_magi_from_membership_frame",
    "medicaid_magi_from_spm",
    "partition_from_existing_id",
]
