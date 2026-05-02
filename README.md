# microunit

`microunit` is Cosilico's unit-assignment package for microdata.

It is part of the Cosilico microdata stack:

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

## Scope

This package should construct unit assignments and explain them. It should not
calculate benefits, taxes, or eligibility amounts. Policy engines remain
responsible for program formulas.

Near-term roadmap:

1. Move reusable SPM unit assignment out of `spm-calculator`.
2. Move reusable tax-unit construction out of `policyengine-us-data` /
   `policyengine-us`.
3. Add CPS and ACS source adapters for Microplex.
4. Use SPM units as the temporary simplification for SNAP, Medicaid/MAGI, and
   other program units.
5. Replace those simplifications with real program rules once Microplex has a
   stable end-to-end unit pipeline.
