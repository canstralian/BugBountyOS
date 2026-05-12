from adapters.airtable.scope_mapper import AirtableScopeAdapter


def test_adapter_initializes_with_expected_base():
    adapter = AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"
    assert adapter.scope_rules_table == "Scope Rules"


def test_get_active_scope_returns_empty_until_wired():
    assert AirtableScopeAdapter().get_active_scope() == []


def test_is_authorized_defaults_to_deny():
    assert AirtableScopeAdapter().is_authorized("anything") is False


# --- Additional edge case and regression tests ---


def test_get_active_scope_returns_list_type():
    result = AirtableScopeAdapter().get_active_scope()
    assert isinstance(result, list)


def test_is_authorized_with_empty_string_asset_id():
    assert AirtableScopeAdapter().is_authorized("") is False


def test_is_authorized_with_various_inputs_always_returns_false():
    adapter = AirtableScopeAdapter()
    for asset_id in ["", "asset-1", "appT4zR1ybxgrujBD", "  ", "!@#$%"]:
        assert adapter.is_authorized(asset_id) is False, f"Expected False for asset_id={asset_id!r}"


def test_adapter_attributes_are_strings():
    adapter = AirtableScopeAdapter()
    assert isinstance(adapter.base_id, str)
    assert isinstance(adapter.scope_rules_table, str)


def test_multiple_adapter_instances_share_same_config():
    a1 = AirtableScopeAdapter()
    a2 = AirtableScopeAdapter()
    assert a1.base_id == a2.base_id
    assert a1.scope_rules_table == a2.scope_rules_table


def test_get_active_scope_returns_new_list_each_call():
    adapter = AirtableScopeAdapter()
    result1 = adapter.get_active_scope()
    result2 = adapter.get_active_scope()
    assert result1 == result2
    # Mutating the result of one call should not affect the other
    result1.append({"fake": "entry"})
    assert adapter.get_active_scope() == []


def test_scope_rules_table_name():
    adapter = AirtableScopeAdapter()
    assert adapter.scope_rules_table == "Scope Rules"
    assert " " in adapter.scope_rules_table
