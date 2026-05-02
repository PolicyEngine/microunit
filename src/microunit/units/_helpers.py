"""Shared helpers for unit adapters."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def first_present_column(frame: pd.DataFrame, columns: Iterable[str]) -> str | None:
    for column in columns:
        if column in frame and not frame[column].isna().any():
            return column
    return None


def composite_ids(frame: pd.DataFrame, *columns: str) -> pd.Series:
    missing = [column for column in columns if column not in frame]
    if missing:
        raise KeyError(f"Missing columns for composite IDs: {missing}")
    values = frame.loc[:, list(columns)].astype("string")
    return values.agg(":".join, axis=1)
