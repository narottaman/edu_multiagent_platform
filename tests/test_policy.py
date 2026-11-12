import pytest
from app.tools.registry import authorize

def test_quiz_cannot_use_web():
    with pytest.raises(PermissionError): authorize("tavily", "quiz", ["canvas:read"])
def test_quiz_canvas_allowed(): authorize("canvas", "quiz", ["canvas:read"])
