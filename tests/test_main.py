import pytest
from unittest.mock import MagicMock, patch, call
from genai_demo.__main__ import automated, interactive
from itertools import chain, repeat

@pytest.fixture
def mock_client():
    return MagicMock()

@patch("genai_demo.__main__.wait_for_new_version")
@patch("genai_demo.__main__.get_artifact")
@patch("genai_demo.__main__.find_param_reqs")
@patch("genai_demo.__main__.print_summary")
@patch("genai_demo.__main__.os.remove")
@patch("genai_demo.__main__.get_failing_params")
@patch("genai_demo.__main__.fix_failing_params")
@patch("genai_demo.__main__.save_params_to_input_json")
@patch("genai_demo.__main__.update_parameters")
@patch("genai_demo.__main__.check_requirement")
@patch("genai_demo.__main__.get_input")
def test_automated_interactive_happy_path(
    mock_get_input,
    mock_check_requirement,
    mock_update_parameters,
    mock_save_params_to_input_json,
    mock_fix_failing_params,
    mock_get_failing_params,
    mock_os_remove,
    mock_print_summary,
    mock_find_param_reqs,
    mock_get_artifact,
    mock_wait_for_new_version,
    mock_client
):
    # Setup mocks
    mock_wait_for_new_version.side_effect = ["new_version", KeyboardInterrupt]
    mock_find_param_reqs.return_value = ["param_req1", "param_req2"]
    # First call: 2 failing params, second call: 0 (all fixed)
    mock_get_failing_params.side_effect = chain(
        [["fail1", "fail2"], []],  # first two calls
        repeat([])                  # all subsequent calls
    )
    mock_fix_failing_params.return_value = [{"name": "foo", "value": "bar"}]

    # Simulate: first loop returns failing param, second loop returns none
    mock_find_param_reqs.side_effect = [
        [("param_obj", "req_obj")],  # first loop: 1 fail
        []                           # second loop: all pass
    ]
    # Simulate user says 'y' to update, then provides a valid value
    mock_get_input.side_effect = ["y"]
    mock_check_requirement.side_effect = [False, True]  # fail, then pass

    # Run
    try:
        automated(mock_client)
    except KeyboardInterrupt:
        pass  # Expected to break the loop for testing

    # Check that get_artifact was called for both requirements and parameters
    assert mock_get_artifact.call_count == 4  # 2 per loop, 2 loops
    # Check that save_params_to_input_json and update_parameters were called
    mock_save_params_to_input_json.assert_called_once()
    mock_update_parameters.assert_called_once()
    # Check that os.remove was called for temp files
    assert mock_os_remove.call_count >= 2

    # Check that the loop exited after requirements were satisfied
    assert mock_get_failing_params.call_count == 2
