import microunit


def test_version():
    assert microunit.__version__ == "0.1.0"


def test_public_api_is_exported():
    for name in (
        "construct_tax_units",
        "HEAD",
        "SPOUSE",
        "DEPENDENT",
        "POLICYENGINE_MODE",
        "CENSUS_DOCUMENTED_MODE",
        "dependent_gross_income_limit",
        "qualifying_child_age_test",
    ):
        assert hasattr(microunit, name), name


def test_unit_role_constants():
    assert microunit.HEAD == "HEAD"
    assert microunit.SPOUSE == "SPOUSE"
    assert microunit.DEPENDENT == "DEPENDENT"


def test_modes():
    assert microunit.POLICYENGINE_MODE == "policyengine"
    assert microunit.CENSUS_DOCUMENTED_MODE == "census_documented"


def test_packaged_yaml_resource_loads():
    # The qualifying-relative gross income limit must resolve from packaged
    # data (importlib.resources), not from any source tree or external
    # dependency.
    assert microunit.dependent_gross_income_limit(2024) == 5_050
    assert microunit.dependent_gross_income_limit(2026) == 5_300
