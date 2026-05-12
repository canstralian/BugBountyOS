from adapters.airtable.scope_mapper import AirtableScopeAdapter


def test_adapter_initializes_with_base_id():
    adapter = AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"
    assert adapter.scope_rules_table == "Scope Rules"


def test_get_active_scope_returns_empty_stub():
    adapter = AirtableScopeAdapter()
    assert adapter.get_active_scope() == []


def test_is_authorized_defaults_closed():
    adapter = AirtableScopeAdapter()
    assert adapter.is_authorized("any-asset") is False
