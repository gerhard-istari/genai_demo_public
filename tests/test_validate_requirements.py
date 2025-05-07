from unittest.mock import patch, MagicMock
import pytest
import genai_demo.components.validate_requirements as vr
from genai_demo.components.validate_requirements import Parameter, Bounds, BoundType

def test_all_validate_requirements_functions():
    with patch("genai_demo.components.validate_requirements.print"), \
         patch("genai_demo.components.validate_requirements.PrettyTable", MagicMock()), \
         patch("genai_demo.components.validate_requirements.get_column_header_color", return_value=""), \
         patch("genai_demo.components.validate_requirements.format_str", side_effect=lambda x, *a, **k: x):
        # Normal cases
        vr.get_failing_params([({"name": "foo", "value": "1"}, {"bounds": "[0;2]"})])
        vr.fix_failing_params([({"name": "foo", "value": "1", "units": "m"}, {"bounds": "[0;2]"})])
        b = vr.Bounds("[0;2]")
        b.get_nearest_passing_value(1)
        # Edge cases
        vr.get_failing_params([])
        vr.fix_failing_params([])
        b = vr.Bounds("")
        with pytest.raises(TypeError):
            b.get_nearest_passing_value(None)
        # Table output
        vr.print_summary([({"name": "foo", "value": "1"}, {"bounds": "[0;2]", "qualified_name": "req1"})])
        vr.print_summary([])
        # Color and format
        vr.get_column_header_color("header")
        vr.format_str("text", 1) 

def test_parameter_and_bounds_branches():
    # Parameter edge cases
    p = Parameter("12.5m")
    assert p.value == 12.5 and p.units == "m"
    assert p.get_value_str() == "12.5m"
    p = Parameter("bad")
    assert p.value == 0.0 and p.units == ""
    # Bounds branches
    b = Bounds("[1;2]")
    assert b.get_type() == BoundType.RANGE
    assert b.is_satisfied(1.5)
    b = Bounds("<5")
    assert b.get_type() == BoundType.LESS_THAN_EQUAL
    assert b.is_satisfied(4.9)
    b = Bounds("<= 5")
    assert b.get_type() == BoundType.LESS_THAN_EQUAL
    assert b.is_satisfied(5)
    b = Bounds("> 1")
    assert b.get_type() == BoundType.GREATER_THAN_EQUAL
    with pytest.raises(TypeError):
        b.is_satisfied(2)
    b = Bounds(">= 1")
    assert b.get_type() == BoundType.GREATER_THAN_EQUAL
    with pytest.raises(TypeError):
        b.is_satisfied(1)
    b = Bounds("= 3")
    assert b.get_lower() == 3 and b.get_upper() == 3
    # get_nearest_passing_value branches
    b = Bounds("[1;2]")
    b.get_nearest_passing_value(0.5)
    b = Bounds("< 5")
    b.get_nearest_passing_value(10)
    b = Bounds("<= 5")
    b.get_nearest_passing_value(10)
    b = Bounds("> 1")
    with pytest.raises(TypeError):
        b.get_nearest_passing_value(0)
    b = Bounds(">= 1")
    with pytest.raises(TypeError):
        b.get_nearest_passing_value(0)
    b = Bounds("= 3")
    b.get_nearest_passing_value(0)
    # parse_bnd_str error case
    b = Bounds("")
    with pytest.raises(TypeError):
        b.is_satisfied(None) 
