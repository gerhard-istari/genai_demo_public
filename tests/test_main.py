import pytest
from unittest.mock import MagicMock, patch, call
from genai_demo.__main__ import automated, interactive
from itertools import chain, repeat
from istari_digital_client.models import JobStatusName
from unittest.mock import mock_open
import builtins
import io
import sys
from contextlib import ExitStack

def log_and_passthrough(name, ret=None):
    def wrapper(*args, **kwargs):
        print(f"[LOG] {name} called with args={args}, kwargs={kwargs}")
        return ret
    return wrapper

@pytest.fixture
def mock_client():
    return MagicMock()

@pytest.mark.timeout(5)
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

@pytest.mark.timeout(5)
def test_interactive_happy_path():
    with patch("genai_demo.__main__.get_artifact"), \
         patch("genai_demo.__main__.find_param_reqs") as mock_find_param_reqs, \
         patch("genai_demo.__main__.print_summary"), \
         patch("genai_demo.__main__.check_requirement") as mock_check_requirement, \
         patch("genai_demo.__main__.get_input") as mock_get_input, \
         patch("genai_demo.__main__.save_params_to_input_json"), \
         patch("genai_demo.__main__.update_parameters"), \
         patch("genai_demo.__main__.os.remove"), \
         patch("builtins.input") as mock_input:
        # Minimal param/req objects
        param_obj = {"name": "foo", "value": "5m"}
        req_obj = {"bounds": ">= 10m"}
        # First call: 1 failing param, second call: all pass
        mock_find_param_reqs.side_effect = [
            [(param_obj, req_obj)],
            []
        ]
        # User says 'y' to update, then provides '10m'
        mock_get_input.side_effect = ["y"]
        mock_input.side_effect = ["10m"]
        # First check fails, second passes
        mock_check_requirement.side_effect = [False, True]
        # Use a MagicMock for the client
        mock_client = MagicMock()
        # Capture printed output
        captured = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        interactive(mock_client)
        sys.stdout = sys_stdout
        output = captured.getvalue()
        # Check for key output
        assert "Retrieving system requirements" in output
        assert "failed requirement(s) found" in output
        assert "Pushing updated parameter values to CAD model" in output
        assert "CAD Parameters satisfy all associated requirements" in output

def make_mock_client():
    revision = MagicMock()
    revision.id = "rev1"
    revision.display_name = "Model Rev 1"
    file = MagicMock()
    file.revisions = [revision]
    model = MagicMock()
    model.file = file
    model.name = "model_file_name"
    art_rev_src = MagicMock()
    art_rev_src.revision_id = "rev1"
    art_rev = MagicMock()
    art_rev.sources = [art_rev_src]
    art_rev.read_bytes.return_value = b"artifact-bytes"
    artifact = MagicMock()
    artifact.name = "requirements.json"
    artifact.revisions = [art_rev]
    artifact.read_bytes.return_value = b"artifact-bytes"
    art_list = MagicMock()
    art_list.items = [artifact]
    job = MagicMock()
    job.id = "job123"
    job.status.name = "COMPLETED"
    client = MagicMock()
    client.get_model.return_value = model
    client.list_model_artifacts.return_value = art_list
    client.add_job.return_value = job
    client.get_job.return_value = job
    client.update_model.return_value = None
    return client

mock_client_instance = make_mock_client()

@pytest.mark.timeout(5)
def test_interactive_high_res():
    def open_side_effect(file, mode='r', *args, **kwargs):
        import io, builtins
        if file == "parameters.json" and 'r' in mode:
            return io.StringIO('[{"parameters": [{"name": "foo", "value": "15"}]}]')
        if file == "requirements.json" and 'r' in mode:
            return io.StringIO('[{"qualified_name": "req1", "bounds": "[10; 20]"}]')
        return builtins.open(file, mode, *args, **kwargs)
    # Helper for completed job mock
    def completed_job_mock():
        job = MagicMock()
        status = MagicMock()
        status.name = JobStatusName.COMPLETED
        job.status = status
        return job
    patches = [
        patch("genai_demo.shared.helpers.get_client"),
        patch("genai_demo.__main__.get_input", return_value="y"),
        patch("genai_demo.__main__.input", return_value="15m"),
        patch("genai_demo.__main__.find_param_reqs", return_value=[({"name": "foo", "value": "15"}, {"bounds": "[10; 20]", "qualified_name": "req1"})]),
        patch("genai_demo.__main__.check_requirement", side_effect=[False, True, True, True, True, True, True, True, True, True]),
        patch("genai_demo.__main__.open", side_effect=open_side_effect),
        patch("istari_digital_client.Client.get_model", return_value=MagicMock(file=MagicMock(read_bytes=MagicMock(return_value=b"artifact-bytes")), name="model_file_name")),
        patch("istari_digital_client.Client.list_model_artifacts", return_value=MagicMock(items=[MagicMock(name="requirements.json", revisions=[MagicMock(sources=[MagicMock(revision_id="rev1")], read_bytes=MagicMock(return_value=b"artifact-bytes"))])])),
        patch("istari_digital_client.Client.add_job", return_value=completed_job_mock()),
        patch("istari_digital_client.Client.get_job", return_value=completed_job_mock()),
        patch("istari_digital_client.Client.update_model", return_value=None),
        patch("genai_demo.shared.helpers.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.components.extract_requirements.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.components.extract_parameters.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.shared.helpers.download_artifact", return_value=None),
        patch("genai_demo.components.extract_requirements.download_artifact", return_value=None),
        patch("genai_demo.components.extract_parameters.download_artifact", return_value=None),
        patch("genai_demo.components.extract_parameters.sleep", return_value=None),
        patch("time.sleep", return_value=None),
        patch("genai_demo.components.update_parameters.submit_job", return_value=completed_job_mock()),
        patch("genai_demo.components.update_parameters.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.__main__.update_parameters", lambda *a, **k: None),
    ]
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        from genai_demo.__main__ import interactive
        interactive(MagicMock())

@pytest.mark.timeout(5)
def test_automated_high_res():
    print("[LOG] test_automated_high_res started")
    mock_client = make_mock_client()
    # Patch get_job and get_model to return objects that break loops
    mock_job = mock_client.add_job.return_value
    mock_job.status.name = "COMPLETED"
    mock_client.get_job.return_value = mock_job
    mock_model = mock_client.get_model.return_value
    mock_model.file.revisions = [
        type('rev', (), {'display_name': 'Model Rev 1', 'id': 'rev1'})(),
        type('rev', (), {'display_name': 'Model Rev 2', 'id': 'rev2'})()
    ]
    with patch("time.sleep", log_and_passthrough("time.sleep")), \
         patch("genai_demo.shared.helpers.sleep", log_and_passthrough("helpers.sleep")), \
         patch("genai_demo.shared.helpers.get_client", return_value=mock_client), \
         patch("genai_demo.__main__.get_input", log_and_passthrough("get_input", ret="y")), \
         patch("builtins.input", log_and_passthrough("input", ret="10m")), \
         patch("genai_demo.__main__.os.remove"), \
         patch("genai_demo.__main__.save_params_to_input_json"), \
         patch("genai_demo.__main__.update_parameters"), \
         patch("genai_demo.__main__.get_artifact"), \
         patch("genai_demo.__main__.find_param_reqs", side_effect=[
             [({"name": "foo", "value": "15"}, {"bounds": "[10; 20]", "qualified_name": "req1"})],  # first loop: 1 fail
             []                            # second loop: all pass
         ]), \
         patch("genai_demo.__main__.get_failing_params", side_effect=[
             [({"name": "foo", "value": "15"}, {"bounds": "[10; 20]", "qualified_name": "req1"})],  # first loop: 1 fail
             []                            # second loop: all pass
         ]), \
         patch("genai_demo.__main__.fix_failing_params", return_value=[{"name": "foo", "value": "bar"}]), \
         patch("genai_demo.__main__.wait_for_new_version", side_effect=["new_version", KeyboardInterrupt]), \
         patch("genai_demo.__main__.check_requirement", side_effect=[False, True, True, True, True, True, True, True, True, True]):
        import io, sys
        from genai_demo.__main__ import automated
        captured = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        try:
            automated(mock_client)
        except KeyboardInterrupt:
            pass
        sys.stdout = sys_stdout
        output = captured.getvalue()
        assert "Retrieving system requirements" in output
        assert "failed requirement(s) found" in output
        assert "Pushing updated parameter values to CAD model" in output
        assert "CAD Parameters satisfy all associated requirements" in output

# Minimal isolation test

@pytest.mark.timeout(5)
def test_minimal_interactive_import_and_call():
    def open_side_effect(file, mode='r', *args, **kwargs):
        import io, builtins
        if file == "parameters.json" and 'r' in mode:
            return io.StringIO('[{"parameters": [{"name": "foo", "value": "15"}]}]')
        if file == "requirements.json" and 'r' in mode:
            return io.StringIO('[{"qualified_name": "req1", "bounds": "[10; 20]"}]')
        return builtins.open(file, mode, *args, **kwargs)
    def completed_job_mock():
        job = MagicMock()
        status = MagicMock()
        status.name = JobStatusName.COMPLETED
        job.status = status
        return job
    patches = [
        patch("genai_demo.shared.helpers.get_client", return_value=MagicMock()),
        patch("genai_demo.__main__.get_input", return_value="y"),
        patch("genai_demo.__main__.input", return_value="15m"),
        patch("genai_demo.__main__.find_param_reqs", return_value=[({"name": "foo", "value": "15"}, {"bounds": "[10; 20]", "qualified_name": "req1"})]),
        patch("genai_demo.__main__.check_requirement", side_effect=[False, True, True, True, True, True, True, True, True, True]),
        patch("genai_demo.__main__.open", side_effect=open_side_effect),
        patch("istari_digital_client.Client.get_model", return_value=MagicMock(file=MagicMock(read_bytes=MagicMock(return_value=b"artifact-bytes")), name="model_file_name")),
        patch("istari_digital_client.Client.list_model_artifacts", return_value=MagicMock(items=[MagicMock(name="requirements.json", revisions=[MagicMock(sources=[MagicMock(revision_id="rev1")], read_bytes=MagicMock(return_value=b"artifact-bytes"))])])),
        patch("istari_digital_client.Client.add_job", return_value=completed_job_mock()),
        patch("istari_digital_client.Client.get_job", return_value=completed_job_mock()),
        patch("istari_digital_client.Client.update_model", return_value=None),
        patch("genai_demo.shared.helpers.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.components.extract_requirements.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.components.extract_parameters.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.shared.helpers.download_artifact", return_value=None),
        patch("genai_demo.components.extract_requirements.download_artifact", return_value=None),
        patch("genai_demo.components.extract_parameters.download_artifact", return_value=None),
        patch("genai_demo.components.extract_parameters.sleep", return_value=None),
        patch("time.sleep", return_value=None),
        patch("genai_demo.components.update_parameters.submit_job", return_value=completed_job_mock()),
        patch("genai_demo.components.update_parameters.wait_for_job", return_value=completed_job_mock()),
        patch("genai_demo.__main__.update_parameters", lambda *a, **k: None),
    ]
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        from genai_demo.__main__ import interactive
        interactive(MagicMock())
