from adapters.airtable.scope_mapper import AirtableScopeAdapter


def test_adapter_initializes_with_expected_base():
    adapter = AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"
    assert adapter.scope_rules_table == "Scope Rules"


def test_get_active_scope_returns_empty_until_wired():
    assert AirtableScopeAdapter().get_active_scope() == []


def test_is_authorized_defaults_to_deny():
    assert AirtableScopeAdapter().is_authorized("anything") is False
