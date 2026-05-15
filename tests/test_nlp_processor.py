"""Tests for vectors/pipeline/nlp_processor.py.

NLPProcessor is imported directly from the pipeline module path to avoid
Flask dependency issues (routes.py and models.py import Flask/app).
"""
import importlib
import sys
from pathlib import Path

import pytest

PIPELINE_PATH = str(Path(__file__).resolve().parents[1] / "vectors" / "pipeline")


@pytest.fixture(autouse=True)
def _add_pipeline_to_path():
    """Temporarily add the pipeline directory to sys.path."""
    sys.path.insert(0, PIPELINE_PATH)
    yield
    sys.path.remove(PIPELINE_PATH)


def _import_nlp():
    if "nlp_processor" in sys.modules:
        del sys.modules["nlp_processor"]
    return importlib.import_module("nlp_processor")


def test_nlp_processor_can_be_instantiated():
    mod = _import_nlp()
    processor = mod.NLPProcessor()
    assert processor is not None


def test_nlp_processor_is_correct_type():
    mod = _import_nlp()
    processor = mod.NLPProcessor()
    assert isinstance(processor, mod.NLPProcessor)


def test_nlp_processor_multiple_instances():
    mod = _import_nlp()
    a = mod.NLPProcessor()
    b = mod.NLPProcessor()
    assert a is not b


def test_nlp_processor_init_takes_no_args():
    mod = _import_nlp()
    # Should not raise when called with no arguments.
    processor = mod.NLPProcessor()
    assert processor is not None


def test_nlp_processor_init_raises_on_extra_positional_args():
    mod = _import_nlp()
    with pytest.raises(TypeError):
        mod.NLPProcessor("unexpected_arg")
