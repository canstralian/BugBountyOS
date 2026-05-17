import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlp_processor import NLPProcessor


def test_stub_returns_well_formed_action_plan():
    proc = NLPProcessor()
    result = proc.process("example.com", [])
    assert result["target"] == "example.com"
    assert isinstance(result["id"], str) and len(result["id"]) == 36  # uuid4
    assert isinstance(result["recommendations"], list)
    assert isinstance(result["confidence"], float)
    assert result["provider"] in ("none", "error", "claude", "mistral")
    assert "timestamp" in result


def test_stub_mode_when_no_keys():
    proc = NLPProcessor()
    proc.anthropic_key = ""
    proc.mistral_key = ""
    result = proc.process("target.io", [{"kind": "port", "value": "443", "confidence": 1.0}])
    assert result["provider"] in ("none", "error")
    assert result["target"] == "target.io"


def test_process_with_findings_list():
    proc = NLPProcessor()
    findings = [
        {"kind": "subdomain", "value": "admin.target.io", "confidence": 0.8},
        {"kind": "port", "value": "8080", "confidence": 1.0},
    ]
    result = proc.process("target.io", findings)
    assert result["target"] == "target.io"
    assert isinstance(result["recommendations"], list)
