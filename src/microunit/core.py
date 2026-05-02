"""Core unit assignment containers."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass

import pandas as pd


def _series(values: pd.Series | Iterable[Hashable], name: str) -> pd.Series:
    if isinstance(values, pd.Series):
        return values.rename(name)
    return pd.Series(list(values), name=name)


@dataclass(frozen=True)
class UnitPartition:
    """A policy-unit assignment with exactly one unit per person."""

    unit_type: str
    person_id: pd.Series
    unit_id: pd.Series
    role: pd.Series | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        person_id = _series(self.person_id, "person_id")
        unit_id = _series(self.unit_id, "unit_id")

        if len(person_id) != len(unit_id):
            raise ValueError("person_id and unit_id must have the same length")
        if person_id.isna().any():
            raise ValueError("person_id cannot contain missing values")
        if unit_id.isna().any():
            raise ValueError("unit_id cannot contain missing values")
        if person_id.duplicated().any():
            duplicates = person_id[person_id.duplicated()].unique().tolist()
            raise ValueError(f"person_id must be unique, found duplicates: {duplicates}")

        object.__setattr__(self, "person_id", person_id.reset_index(drop=True))
        object.__setattr__(self, "unit_id", unit_id.reset_index(drop=True))

        if self.role is not None:
            role = _series(self.role, "role")
            if len(role) != len(person_id):
                raise ValueError("role must have the same length as person_id")
            object.__setattr__(self, "role", role.reset_index(drop=True))

    @classmethod
    def from_frame(
        cls,
        frame: pd.DataFrame,
        unit_type: str,
        person_col: str = "person_id",
        unit_col: str = "unit_id",
        role_col: str | None = None,
        source: str | None = None,
    ) -> UnitPartition:
        """Build a partition from columns in a person-level frame."""

        role = frame[role_col] if role_col is not None else None
        return cls(
            unit_type=unit_type,
            person_id=frame[person_col],
            unit_id=frame[unit_col],
            role=role,
            source=source,
        )

    @property
    def n_persons(self) -> int:
        return len(self.person_id)

    @property
    def n_units(self) -> int:
        return int(self.unit_id.nunique())

    def to_frame(self) -> pd.DataFrame:
        """Return person-level unit assignments."""

        frame = pd.DataFrame(
            {
                "person_id": self.person_id,
                "unit_id": self.unit_id,
            }
        )
        if self.role is not None:
            frame["role"] = self.role
        return frame

    def members(self) -> dict[Hashable, tuple[Hashable, ...]]:
        """Return unit members keyed by unit ID."""

        frame = self.to_frame()
        grouped = frame.groupby("unit_id", sort=False)["person_id"]
        return {unit_id: tuple(group.tolist()) for unit_id, group in grouped}

    def unit_sizes(self) -> pd.Series:
        """Return the number of people in each unit."""

        return self.unit_id.value_counts(sort=False)

    def relabel(self, prefix: str = "unit_") -> UnitPartition:
        """Return a copy with dense, stable unit IDs in encounter order."""

        codes = pd.factorize(self.unit_id, sort=False)[0]
        unit_id = pd.Series([f"{prefix}{code + 1}" for code in codes])
        return UnitPartition(
            unit_type=self.unit_type,
            person_id=self.person_id,
            unit_id=unit_id,
            role=self.role,
            source=self.source,
        )


@dataclass(frozen=True)
class EgoUnitMembership:
    """A possibly-overlapping unit assignment for each focal person."""

    unit_type: str
    focal_person_id: pd.Series
    member_person_id: pd.Series
    role: pd.Series | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        focal = _series(self.focal_person_id, "focal_person_id")
        member = _series(self.member_person_id, "member_person_id")

        if len(focal) != len(member):
            raise ValueError("focal_person_id and member_person_id must align")
        if focal.isna().any() or member.isna().any():
            raise ValueError("ego unit memberships cannot contain missing IDs")

        pairs = pd.DataFrame({"focal": focal, "member": member})
        if pairs.duplicated().any():
            raise ValueError("ego unit memberships cannot contain duplicate pairs")

        object.__setattr__(self, "focal_person_id", focal.reset_index(drop=True))
        object.__setattr__(self, "member_person_id", member.reset_index(drop=True))

        if self.role is not None:
            role = _series(self.role, "role")
            if len(role) != len(focal):
                raise ValueError("role must have the same length as memberships")
            object.__setattr__(self, "role", role.reset_index(drop=True))

    @classmethod
    def from_mapping(
        cls,
        unit_type: str,
        memberships: Mapping[Hashable, Iterable[Hashable]],
        source: str | None = None,
    ) -> EgoUnitMembership:
        """Build overlapping units from focal-person membership sets."""

        focal_ids: list[Hashable] = []
        member_ids: list[Hashable] = []
        for focal, members in memberships.items():
            for member in members:
                focal_ids.append(focal)
                member_ids.append(member)
        return cls(unit_type, pd.Series(focal_ids), pd.Series(member_ids), source=source)

    def to_frame(self) -> pd.DataFrame:
        """Return membership rows keyed by focal person and member person."""

        frame = pd.DataFrame(
            {
                "focal_person_id": self.focal_person_id,
                "member_person_id": self.member_person_id,
            }
        )
        if self.role is not None:
            frame["role"] = self.role
        return frame

    def members_for(self, focal_person_id: Hashable) -> tuple[Hashable, ...]:
        frame = self.to_frame()
        members = frame.loc[
            frame["focal_person_id"] == focal_person_id, "member_person_id"
        ]
        return tuple(members.tolist())
