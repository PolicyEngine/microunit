import pandas as pd
import pytest

from microunit import EgoUnitMembership, UnitPartition


def test_unit_partition_groups_members():
    partition = UnitPartition(
        unit_type="tax",
        person_id=pd.Series([1, 2, 3]),
        unit_id=pd.Series([10, 10, 11]),
    )

    assert partition.n_persons == 3
    assert partition.n_units == 2
    assert partition.members() == {10: (1, 2), 11: (3,)}


def test_unit_partition_rejects_duplicate_person_ids():
    with pytest.raises(ValueError, match="person_id must be unique"):
        UnitPartition(
            unit_type="tax",
            person_id=pd.Series([1, 1]),
            unit_id=pd.Series([10, 11]),
        )


def test_ego_unit_membership_allows_overlaps():
    membership = EgoUnitMembership.from_mapping(
        "medicaid_magi",
        {
            1: [1, 2, 3],
            2: [1, 2],
        },
    )

    assert membership.members_for(1) == (1, 2, 3)
    assert membership.members_for(2) == (1, 2)
