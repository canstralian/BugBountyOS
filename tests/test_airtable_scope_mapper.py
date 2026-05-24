from adapters.airtable.scope_mapper import AirtableScopeAdapter


def test_adapter_initializes_with_expected_base():
    adapter = AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"
    assert adapter.scope_rules_table == "Scope Rules"


def test_get_active_scope_returns_empty_until_wired():
    assert AirtableScopeAdapter().get_active_scope() == []


def test_is_authorized_defaults_to_deny():
    assert AirtableScopeAdapter().is_authorized("anything") is False


def test_base_id_is_string():
    adapter = AirtableScopeAdapter()
    assert isinstance(adapter.base_id, str)


def test_scope_rules_table_is_string():
    adapter = AirtableScopeAdapter()
    assert isinstance(adapter.scope_rules_table, str)


def test_get_active_scope_returns_list_type():
    result = AirtableScopeAdapter().get_active_scope()
    assert isinstance(result, list)


def test_is_authorized_returns_false_for_empty_string():
    assert AirtableScopeAdapter().is_authorized("") is False


def test_is_authorized_returns_false_for_numeric_string():
    assert AirtableScopeAdapter().is_authorized("12345") is False


def test_is_authorized_returns_bool():
    result = AirtableScopeAdapter().is_authorized("some-asset")
    assert isinstance(result, bool)


def test_multiple_instances_are_independent():
    a = AirtableScopeAdapter()
    b = AirtableScopeAdapter()
    assert a.base_id == b.base_id
    assert a.scope_rules_table == b.scope_rules_table
    assert a is not b


def test_get_active_scope_is_idempotent():
    adapter = AirtableScopeAdapter()
    first = adapter.get_active_scope()
    second = adapter.get_active_scope()
    assert first == second


def test_is_authorized_consistent_for_same_input():
    adapter = AirtableScopeAdapter()
    asset = "recXYZ123"
    assert adapter.is_authorized(asset) == adapter.is_authorized(asset)


def test_adapter_base_id_matches_readme():
    # Confirms the hardcoded base ID matches the documented Airtable base.
    adapter = AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"


def test_scope_rules_table_name():
    # Confirms the table name matches the documented Airtable table.
    adapter = AirtableScopeAdapter()
    assert adapter.scope_rules_table == "Scope Rules"
