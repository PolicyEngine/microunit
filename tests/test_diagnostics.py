import pandas as pd

from microunit import UnitPartition, partition_match_report


def test_partition_match_report_ignores_arbitrary_unit_labels():
    reference = UnitPartition(
        "spm",
        person_id=pd.Series([1, 2, 3, 4]),
        unit_id=pd.Series([10, 10, 11, 20]),
    )
    candidate = UnitPartition(
        "spm",
        person_id=pd.Series([1, 2, 3, 4]),
        unit_id=pd.Series(["a", "a", "b", "z"]),
    )
    group_id = pd.Series([100, 100, 100, 101])

    report = partition_match_report(reference, candidate, group_id)

    assert report.group_count == 2
    assert report.group_match_rate == 1
    assert report.person_match_rate == 1


def test_partition_match_report_flags_changed_partition():
    reference = UnitPartition(
        "spm",
        person_id=pd.Series([1, 2, 3]),
        unit_id=pd.Series([10, 10, 11]),
    )
    candidate = UnitPartition(
        "spm",
        person_id=pd.Series([1, 2, 3]),
        unit_id=pd.Series([10, 11, 11]),
    )
    group_id = pd.Series([100, 100, 100])

    report = partition_match_report(reference, candidate, group_id)

    assert report.group_match_rate == 0
    assert report.person_match_rate == 0
