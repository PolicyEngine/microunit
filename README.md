# microunit

`microunit` is PolicyEngine's unit-assignment package for microdata.

It is part of the PolicyEngine microdata stack:

- `microimpute`: fill missing variables and transfer attributes across data
  sources.
- `microcalibrate`, eventually maybe `microweight`: align microdata to external
  targets.
- `microunit`: construct policy units from person and relationship records.
- `microplex`: synthesize, rebuild, and evaluate full microdata systems.

It separates "who belongs with whom" from benefit and tax formulas. The same
person table can have several policy units layered on top of it:

- SPM units for poverty measurement.
- Tax units for filing and dependency rules.
- SNAP units for food assistance eligibility.
- Medicaid MAGI households, which are usually focal-person units rather than a
  single partition of the household.

The package starts with the common primitives those systems need:

- `UnitPartition`: one unit ID per person, useful for SPM, tax, and many SNAP
  assignment outputs.
- `EgoUnitMembership`: one membership set per focal person, useful for MAGI-like
  rules where units can overlap.
- SPM simplification adapters for programs whose true unit rules are not yet
  implemented.
- Diagnostics for comparing partitions within households.
- Conservative adapters that preserve existing unit IDs from source data.

## Install

```bash
uv pip install -e ".[dev]"
```

## Example

```python
import pandas as pd
from microunit.units import assign_spm_partition

persons = pd.DataFrame(
    {
        "person_id": [1, 2, 3],
        "household_id": [10, 10, 10],
        "family_id": [100, 100, 101],
    }
)

partition = assign_spm_partition(persons)
print(partition.to_frame())
```

## Rules-based tax-unit construction

`microunit` includes the rules-based tax-unit / filing-status construction
engine extracted from
[`policyengine-us-data`](https://github.com/PolicyEngine/policyengine-us-data).
It applies federal filing and dependency rules to assign people into tax
units, infer each person's role (head / spouse / dependent), and infer a
filing status per unit. It is the same engine reused across the CPS and ACS
pipelines there, and is **source-agnostic**: it operates on
already-normalized, CPS-like person frames. It is consumed by
`policyengine-us-data` and `microplex-us`.

```python
import pandas as pd
from microunit import construct_tax_units

# person uses CPS-like column names (see "Input contract" below).
person_assignments, tax_unit = construct_tax_units(person, year=2024)
```

`construct_tax_units(person, year, mode="policyengine")` returns:

- **`person_assignments`** (indexed like the input): `TAX_ID` (`int64`,
  dense 1-based id), `tax_unit_role_input` (bytes: `HEAD` / `SPOUSE` /
  `DEPENDENT`), `is_related_to_head_or_spouse` (bool).
- **`tax_unit`** (one row per `TAX_ID`): `filing_status_input` (bytes:
  `JOINT` / `HEAD_OF_HOUSEHOLD` / `SURVIVING_SPOUSE` / `SEPARATE` /
  `SINGLE`).

The string columns are byte strings (the HDF5-friendly encoding used by the
source pipeline); decode with `.decode()`.

A `UnitPartition` adapter is also provided:

```python
from microunit.units import construct_tax_partition

partition = construct_tax_partition(person, year=2024)  # UnitPartition(unit_type="tax")
```

### Modes

- **`"policyengine"`** (default, `microunit.POLICYENGINE_MODE`): PolicyEngine's
  dependency/filing-rule flow.
- **`"census_documented"`** (`microunit.CENSUS_DOCUMENTED_MODE`): the publicly
  documented Census tax-model flow.

### Input contract

Required CPS columns (raises `KeyError` if missing): `PH_SEQ`, `A_LINENO`,
`A_AGE`, `A_MARITL`, `A_SPOUSE`, `PEPAR1`, `PEPAR2`, `A_EXPRRP`.

Optional evidence columns (used when present, safely defaulted otherwise):
income components (`WSAL_VAL`, `SEMP_VAL`, `FRSE_VAL`, `INT_VAL`, `DIV_VAL`,
`RNT_VAL`, `CAP_VAL`, `UC_VAL`, `OI_VAL`, `ANN_VAL`, `PNSN_VAL`, `SS_VAL`),
total money income (`PTOTVAL`), enrollment (`A_ENRLW`, `A_FTPT`, `A_HSCOL`),
and disability flags (`PEDISDRS`, `PEDISEAR`, `PEDISEYE`, `PEDISOUT`,
`PEDISPHY`, `PEDISREM`). Relationship codes follow the CPS ASEC `A_EXPRRP`
recode, exposed as `microunit.CPSRelationshipCode`.

### ACS column mapping is the consumer's responsibility

The ACS PUMS -> CPS column mapping (`acs_to_cps_columns.py` in
`policyengine-us-data`) is **not** part of `microunit`. That ~500-line module
is ACS-PUMS-specific (`RELSHIPP`/`RELP` translation, marital-status recoding,
and heuristic spouse/parent-pointer inference, since ACS provides no universal
spouse or parent pointers) and belongs with the ACS reader. Consumers reading
ACS should map their PUMS columns onto the CPS-like contract above and then
call `construct_tax_units`. Accordingly, the ACS-specific tests from
`policyengine-us-data` remain there; the full CPS construction test suite is
ported here.

### Packaged data

The qualifying-relative gross income limit (the personal/dependent exemption
amount under IRC 151(d), used by the IRC 152(d)(1)(B) gross income test) ships
as package data at `microunit/data/dependent_gross_income_limit.yaml` and is
loaded via `importlib.resources`, so the engine does not depend on
`policyengine-us` being installed.

## Scope

This package should construct unit assignments and explain them. It should not
calculate benefits, taxes, or eligibility amounts. Policy engines remain
responsible for program formulas.

Near-term roadmap:

1. Move reusable SPM unit assignment out of `spm-calculator`.
2. Move reusable tax-unit construction out of `policyengine-us-data` /
   `policyengine-us`. (Done -- see "Rules-based tax-unit construction" above.)
3. Add CPS and ACS source adapters for Microplex.
4. Use SPM units as the temporary simplification for SNAP, Medicaid/MAGI, and
   other program units.
5. Replace those simplifications with real program rules once Microplex has a
   stable end-to-end unit pipeline.
