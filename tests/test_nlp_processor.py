"""Tests for vectors/pipeline/nlp_processor.py.

NLPProcessor is a stub class with only __init__ defined (no external deps).
We import it via sys.path since vectors/pipeline has no package __init__.py.
"""
import sys
from pathlib import Path

# Make vectors/pipeline importable as a plain directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vectors" / "pipeline"))

from nlp_processor import NLPProcessor  # noqa: E402


def test_nlp_processor_can_be_instantiated():
    processor = NLPProcessor()
    assert processor is not None


def test_nlp_processor_is_correct_type():
    processor = NLPProcessor()
    assert isinstance(processor, NLPProcessor)


def test_nlp_processor_init_has_no_attributes():
    """The stub __init__ sets no attributes, so __dict__ should be empty."""
    processor = NLPProcessor()
    assert processor.__dict__ == {}


def test_nlp_processor_multiple_instances_are_independent():
    p1 = NLPProcessor()
    p2 = NLPProcessor()
    assert p1 is not p2


def test_nlp_processor_class_name():
    assert NLPProcessor.__name__ == "NLPProcessor"
