import pandas as pd
import pytest

from microunit.units import (
    assign_snap_partition,
    assign_spm_partition,
    assign_tax_partition,
    medicaid_magi_from_membership_frame,
    medicaid_magi_from_spm,
)


def test_spm_partition_preserves_native_ids():
    persons = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "SPM_ID": [100, 100, 200],
        }
    )

    partition = assign_spm_partition(persons)

    assert partition.source == "SPM_ID"
    assert partition.members() == {100: (1, 2), 200: (3,)}


def test_spm_partition_falls_back_to_family_within_household():
    persons = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "household_id": [10, 10, 10],
            "family_id": [1, 1, 2],
        }
    )

    partition = assign_spm_partition(persons)

    assert partition.members() == {"10:1": (1, 2), "10:2": (3,)}


def test_tax_partition_requires_existing_id():
    persons = pd.DataFrame({"person_id": [1, 2]})

    with pytest.raises(KeyError, match="No tax-unit ID column"):
        assign_tax_partition(persons)


def test_tax_partition_preserves_role_inputs():
    persons = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "person_tax_unit_id": [100, 100, 101],
            "tax_unit_role_input": ["head", "spouse", "head"],
        }
    )

    partition = assign_tax_partition(persons)

    assert partition.to_frame()["role"].tolist() == ["head", "spouse", "head"]


def test_snap_partition_uses_spm_simplification_by_default():
    persons = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "household_id": [10, 10, 10],
            "family_id": [1, 1, 2],
        }
    )

    partition = assign_snap_partition(persons)

    assert partition.source == "spm_simplification:household_id+family_id"
    assert partition.members() == {"10:1": (1, 2), "10:2": (3,)}


def test_snap_partition_can_require_native_id():
    persons = pd.DataFrame({"person_id": [1, 2], "household_id": [10, 10]})

    with pytest.raises(KeyError, match="No SNAP unit ID column"):
        assign_snap_partition(persons, use_spm_simplification=False)


def test_medicaid_magi_membership_frame_allows_overlap():
    frame = pd.DataFrame(
        {
            "focal_person_id": [1, 1, 2, 2],
            "member_person_id": [1, 2, 1, 2],
        }
    )

    units = medicaid_magi_from_membership_frame(frame)

    assert units.members_for(1) == (1, 2)
    assert units.members_for(2) == (1, 2)


def test_medicaid_magi_spm_simplification_is_focal_person_membership():
    persons = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "household_id": [10, 10, 10],
            "family_id": [1, 1, 2],
        }
    )

    units = medicaid_magi_from_spm(persons)

    assert units.source == "spm_simplification:household_id+family_id"
    assert units.members_for(1) == (1, 2)
    assert units.members_for(2) == (1, 2)
    assert units.members_for(3) == (3,)
