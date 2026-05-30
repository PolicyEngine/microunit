import numpy as np
import pandas as pd

from microunit import UnitPartition
from microunit.units import construct_tax_partition


def _person_fixture(**overrides):
    n = max((len(value) for value in overrides.values()), default=1)
    defaults = {
        "PH_SEQ": np.ones(n, dtype=int),
        "A_LINENO": np.arange(1, n + 1, dtype=int),
        "A_AGE": np.zeros(n, dtype=int),
        "A_MARITL": np.full(n, 7, dtype=int),
        "A_SPOUSE": np.zeros(n, dtype=int),
        "PEPAR1": np.full(n, -1, dtype=int),
        "PEPAR2": np.full(n, -1, dtype=int),
        "A_EXPRRP": np.full(n, 14, dtype=int),
        "WSAL_VAL": np.zeros(n, dtype=float),
    }
    defaults.update(overrides)
    return pd.DataFrame(defaults)


def test_construct_tax_partition_returns_unit_partition_with_roles():
    person = _person_fixture(
        person_id=[101, 102, 103],
        A_AGE=[40, 38, 8],
        A_MARITL=[1, 1, 7],
        A_SPOUSE=[2, 1, 0],
        A_EXPRRP=[1, 4, 5],
        PEPAR1=[-1, -1, 1],
        PEPAR2=[-1, -1, 2],
        WSAL_VAL=[60_000, 20_000, 0],
    )

    partition = construct_tax_partition(person, year=2024)

    assert isinstance(partition, UnitPartition)
    assert partition.unit_type == "tax"
    assert partition.source == "construct_tax_units:policyengine"
    assert partition.n_units == 1
    frame = partition.to_frame()
    assert frame["person_id"].tolist() == [101, 102, 103]
    assert frame["role"].tolist() == ["HEAD", "SPOUSE", "DEPENDENT"]


def test_construct_tax_partition_defaults_person_id_when_absent():
    person = _person_fixture(
        A_AGE=[45, 22],
        A_EXPRRP=[1, 5],
        PEPAR1=[-1, 1],
        WSAL_VAL=[70_000, 10_000],
    )

    partition = construct_tax_partition(person, year=2024)

    assert partition.n_units == 2
    assert partition.to_frame()["person_id"].tolist() == [0, 1]


def test_construct_tax_partition_supports_census_documented_mode():
    person = _person_fixture(
        person_id=[1, 2],
        A_AGE=[40, 12],
        A_EXPRRP=[1, 14],
        WSAL_VAL=[50_000, 0],
        PTOTVAL=[50_000, 0],
    )

    partition = construct_tax_partition(person, year=2024, mode="census_documented")

    assert partition.source == "construct_tax_units:census_documented"
    assert partition.n_units == 1
    assert partition.to_frame()["role"].tolist() == ["HEAD", "DEPENDENT"]
