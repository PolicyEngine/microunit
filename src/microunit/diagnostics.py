"""Diagnostics for comparing unit assignments."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

import pandas as pd

from microunit.core import UnitPartition


@dataclass(frozen=True)
class PartitionMatchReport:
    """Household-level comparison between two partitions."""

    group_count: int
    matched_group_count: int
    person_count: int
    persons_in_matched_groups: int

    @property
    def group_match_rate(self) -> float:
        if self.group_count == 0:
            return 0.0
        return self.matched_group_count / self.group_count

    @property
    def person_match_rate(self) -> float:
        if self.person_count == 0:
            return 0.0
        return self.persons_in_matched_groups / self.person_count


def _signature(person_id: pd.Series, unit_id: pd.Series) -> frozenset[frozenset[Hashable]]:
    frame = pd.DataFrame({"person_id": person_id, "unit_id": unit_id})
    return frozenset(
        frozenset(group["person_id"].tolist())
        for _, group in frame.groupby("unit_id", sort=False)
    )


def partition_match_report(
    reference: UnitPartition,
    candidate: UnitPartition,
    group_id: pd.Series,
) -> PartitionMatchReport:
    """Compare two partitions within household-like groups.

    Unit IDs are arbitrary labels, so this compares each group's partition of
    people rather than literal unit ID values.
    """

    group_id = group_id.rename("group_id")
    if len(group_id) != reference.n_persons:
        raise ValueError("group_id must have the same length as the reference")

    ref = reference.to_frame().rename(columns={"unit_id": "reference_unit_id"})
    cand = candidate.to_frame().rename(columns={"unit_id": "candidate_unit_id"})
    frame = ref.merge(cand, on="person_id", how="inner", validate="one_to_one")
    if len(frame) != reference.n_persons:
        raise ValueError("reference and candidate must contain the same person IDs")

    frame["group_id"] = group_id.reset_index(drop=True)

    matched_groups = 0
    persons_in_matched_groups = 0
    for _, group in frame.groupby("group_id", sort=False):
        ref_sig = _signature(group["person_id"], group["reference_unit_id"])
        cand_sig = _signature(group["person_id"], group["candidate_unit_id"])
        if ref_sig == cand_sig:
            matched_groups += 1
            persons_in_matched_groups += len(group)

    return PartitionMatchReport(
        group_count=int(frame["group_id"].nunique()),
        matched_group_count=matched_groups,
        person_count=len(frame),
        persons_in_matched_groups=persons_in_matched_groups,
    )
