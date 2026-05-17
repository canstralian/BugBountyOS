VALID_FINDING = {
    "target": "example.com",
    "severity": "high",
    "title": "Open redirect",
    "description": "The /redirect endpoint does not validate the destination URL.",
}


# --- Health ---

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["vector"] == "storage"


# --- Findings ---

def test_create_finding(client):
    r = client.post("/api/findings", json=VALID_FINDING)
    assert r.status_code == 201
    data = r.get_json()
    assert data["target"] == "example.com"
    assert data["severity"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_create_finding_missing_fields(client):
    r = client.post("/api/findings", json={"target": "example.com"})
    assert r.status_code == 422
    assert "Missing required fields" in r.get_json()["error"]


def test_create_finding_no_body(client):
    r = client.post("/api/findings", content_type="application/json")
    assert r.status_code == 400


def test_list_findings_empty(client):
    r = client.get("/api/findings")
    assert r.status_code == 200
    assert r.get_json() == []


def test_list_findings_after_create(client):
    client.post("/api/findings", json=VALID_FINDING)
    client.post("/api/findings", json={**VALID_FINDING, "title": "XSS in search"})
    r = client.get("/api/findings")
    assert r.status_code == 200
    assert len(r.get_json()) == 2


def test_get_finding_by_id(client):
    create_r = client.post("/api/findings", json=VALID_FINDING)
    finding_id = create_r.get_json()["id"]
    r = client.get(f"/api/findings/{finding_id}")
    assert r.status_code == 200
    assert r.get_json()["id"] == finding_id


def test_get_finding_not_found(client):
    r = client.get("/api/findings/9999")
    assert r.status_code == 404


# --- Append-only invariant: no DELETE or UPDATE routes ---

def test_no_delete_findings(client):
    r = client.delete("/api/findings/1")
    assert r.status_code == 405


def test_no_put_findings(client):
    r = client.put("/api/findings/1", json=VALID_FINDING)
    assert r.status_code == 405


def test_no_patch_findings(client):
    r = client.patch("/api/findings/1", json={"status": "submitted"})
    assert r.status_code == 405


# --- Evidence ---

def test_create_evidence(client):
    r = client.post("/api/evidence", json={"kind": "screenshot", "value": "base64data=="})
    assert r.status_code == 201
    data = r.get_json()
    assert data["kind"] == "screenshot"
    assert "id" in data


def test_create_evidence_missing_fields(client):
    r = client.post("/api/evidence", json={"kind": "screenshot"})
    assert r.status_code == 422


def test_list_evidence(client):
    client.post("/api/evidence", json={"kind": "log", "value": "GET /admin 200"})
    r = client.get("/api/evidence")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


# --- Tool runs ---

def test_create_tool_run(client):
    r = client.post("/api/tool-runs", json={"tool": "nmap", "target": "example.com"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["tool"] == "nmap"
    assert data["status"] == "running"


def test_create_tool_run_missing_fields(client):
    r = client.post("/api/tool-runs", json={"tool": "nmap"})
    assert r.status_code == 422


def test_list_tool_runs(client):
    client.post("/api/tool-runs", json={"tool": "nmap", "target": "example.com"})
    r = client.get("/api/tool-runs")
    assert r.status_code == 200
    assert len(r.get_json()) == 1
