import json


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["vector"] == "pipeline"


def test_ingest_event_no_body(client):
    r = client.post("/api/events", content_type="application/json")
    assert r.status_code == 400


def test_ingest_event_missing_target(client):
    r = client.post("/api/events", json={"findings": []})
    assert r.status_code == 422
    assert "target" in r.get_json()["error"]


def test_ingest_event_findings_not_list(client):
    r = client.post("/api/events", json={"target": "example.com", "findings": "bad"})
    assert r.status_code == 422


def test_ingest_event_success(client):
    payload = {
        "target": "example.com",
        "findings": [{"kind": "subdomain", "value": "api.example.com", "confidence": 0.9}],
        "timestamp": "2026-05-09T00:00:00Z",
    }
    r = client.post("/api/events", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data["target"] == "example.com"
    assert "id" in data
    assert "recommendations" in data
    assert "confidence" in data
    assert "provider" in data
    assert "timestamp" in data


def test_ingest_event_empty_findings_accepted(client):
    r = client.post("/api/events", json={"target": "example.com", "findings": []})
    assert r.status_code == 201
