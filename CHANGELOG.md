# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

## [0.1.0] - 2026-05-30

### Added

- Initial release. Rules-based tax-unit construction engine (`construct_tax_units`, `policyengine` and `census_documented` modes) extracted from policyengine-us-data, conservative SPM/SNAP/Medicaid-MAGI unit adapters, partition primitives (`UnitPartition`, `EgoUnitMembership`), and partition-match diagnostics.
