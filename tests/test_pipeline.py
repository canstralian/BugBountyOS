from vectors.pipeline.app import app
from vectors.pipeline.nlp_processor import NLPProcessor


def test_pipeline_app_is_flask_instance():
    assert app.name == "vectors.pipeline.app"


def test_health_endpoint_returns_ok():
    import vectors.pipeline.routes  # noqa: F401  (registers route on app)

    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_nlp_processor_constructs():
    NLPProcessor()
