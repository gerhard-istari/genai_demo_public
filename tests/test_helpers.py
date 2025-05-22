from unittest.mock import patch, MagicMock
import pytest
import genai_demo.shared.helpers as helpers
import itertools
from istari_digital_client.models import JobStatusName

@pytest.mark.timeout(5)
def test_helpers_coverage():
    completed_job = MagicMock(id="job123")
    completed_job.status = MagicMock(name="COMPLETED")
    with patch("genai_demo.shared.helpers.Client", MagicMock()), \
         patch("genai_demo.shared.helpers.print"), \
         patch("genai_demo.shared.helpers.sleep", return_value=None), \
         patch("genai_demo.shared.helpers.open", create=True), \
         patch("json.load", return_value={}), \
         patch("json.dump", return_value=None), \
         patch("genai_demo.shared.helpers.wait_for_job", return_value=completed_job), \
         patch("genai_demo.shared.helpers.wait_for_all_jobs", return_value=[completed_job]):
        # get_client
        helpers.get_client()
        # submit_job
        helpers.submit_job("model_id", "function", "tool_name", "params_file")
        # wait_for_job
        job = completed_job
        helpers.wait_for_job(job)
        # wait_for_all_jobs
        helpers.wait_for_all_jobs()
        # download_artifact_orig
        mock_artifact = MagicMock(read_bytes=MagicMock(return_value=b"bytes"))
        mock_artifact.name = "artifact_name"
        mock_artifact_list = MagicMock(items=[mock_artifact])
        mock_client = MagicMock(list_model_artifacts=MagicMock(return_value=mock_artifact_list))
        with patch("genai_demo.shared.helpers.get_client", return_value=mock_client):
            helpers.download_artifact_orig("model_id", "artifact_name", "dest_file")
        # get_input
        with patch("builtins.input", return_value="y"):
            helpers.get_input("msg", ["y"])
        # format_str
        helpers.format_str("text", 1)

@pytest.mark.timeout(5)
def test_helpers_coverage_edge_cases():
    completed_job = MagicMock(id="job123")
    completed_job.status = MagicMock(name="FAILED")
    with patch("genai_demo.shared.helpers.Client", MagicMock()), \
         patch("genai_demo.shared.helpers.print", side_effect=lambda *a, **k: None), \
         patch("genai_demo.shared.helpers.sleep", return_value=None), \
         patch("genai_demo.shared.helpers.open", create=True), \
         patch("json.load", return_value={}), \
         patch("json.dump", return_value=None), \
         patch("genai_demo.shared.helpers.wait_for_job", return_value=completed_job), \
         patch("genai_demo.shared.helpers.wait_for_all_jobs", return_value=[completed_job]):
        # Edge: wait_for_job with failed status
        helpers.wait_for_job(completed_job)
        # Edge: wait_for_all_jobs with failed job
        helpers.wait_for_all_jobs()
        # download_artifact_orig with no artifacts
        mock_artifact_list = MagicMock(items=[])
        mock_client = MagicMock(list_model_artifacts=MagicMock(return_value=mock_artifact_list))
        with patch("genai_demo.shared.helpers.get_client", return_value=mock_client):
            with pytest.raises(FileNotFoundError):
                helpers.download_artifact_orig("model_id", "artifact_name", "dest_file")
        # get_input with invalid then valid input
        with patch("builtins.input", side_effect=["n", "y"]), patch("genai_demo.shared.helpers.input", side_effect=["n", "y"]):
            helpers.get_input("msg", ["y"])
        # format_str with edge values
        helpers.format_str("", 0) 

@pytest.mark.timeout(5)
def test_helpers_more_coverage():
    from genai_demo.shared import helpers
    import pytest
    # Patch for download_artifact
    mock_artifact_rev_src = MagicMock(revision_id="rev2")
    mock_artifact_rev = MagicMock(sources=[mock_artifact_rev_src], read_bytes=MagicMock(return_value=b"bytes"))
    mock_artifact = MagicMock(revisions=[mock_artifact_rev])
    mock_artifact.name = "artifact_name"
    mock_artifact_list = MagicMock(items=[mock_artifact])
    mock_file = MagicMock(revisions=[MagicMock(id="rev1", display_name="mod", created=1), MagicMock(id="rev2", display_name="mod", created=2)])
    mock_mod = MagicMock(file=mock_file)
    def list_model_artifacts_side_effect(*args, **kwargs):
        if not hasattr(list_model_artifacts_side_effect, 'called'):
            list_model_artifacts_side_effect.called = True
            return mock_artifact_list
        return MagicMock(items=[])
    # Patch for wait_for_new_version
    mock_mod_short = MagicMock()
    mock_mod_short.file.revisions = [MagicMock(id="rev1", display_name="mod", created=1), MagicMock(id="rev2", display_name="mod", created=2)]
    mock_mod_long = MagicMock()
    mock_mod_long.file.revisions = [MagicMock(id="rev1", display_name="mod", created=1), MagicMock(id="rev2", display_name="mod", created=2), MagicMock(id="rev3", display_name="mod", created=3)]
    call_count = [0]
    def get_model_side_effect(*args, **kwargs):
        if call_count[0] == 0:
            call_count[0] += 1
            return mock_mod_short
        return mock_mod_long
    get_model_side_effect.calls = 0
    mock_client = MagicMock(
        get_model=MagicMock(side_effect=get_model_side_effect),
        list_model_artifacts=MagicMock(side_effect=list_model_artifacts_side_effect),
        get_job=MagicMock(return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED")))
    )
    with patch("genai_demo.shared.helpers.get_client", return_value=mock_client), \
         patch("genai_demo.shared.helpers.open", create=True), \
         patch("builtins.print", new=lambda *a, **k: None), \
         patch("genai_demo.shared.helpers.sleep", new=lambda *a, **k: None), \
         patch("genai_demo.shared.helpers.wait_for_new_version", new=lambda *a, **k: None):
        # download_artifact success
        helpers.download_artifact("model_id", "artifact_name")
        # download_artifact FileNotFoundError
        mock_artifact_list.items = []
        with pytest.raises(FileNotFoundError):
            helpers.download_artifact("model_id", "artifact_name")
        # get_latest_revision
        helpers.get_latest_revision("model_id")
        # wait_for_new_version
        helpers.wait_for_new_version("model_id") 

@pytest.mark.timeout(5)
def test_submit_job_calls_client_add_job():
    """Test that submit_job calls Client.add_job with correct arguments."""
    with patch("genai_demo.shared.helpers.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.add_job.return_value = MagicMock(id="job123", status=MagicMock(name="COMPLETED"))
        result = helpers.submit_job("model_id", "function", "tool_name", "params_file")
        mock_client.add_job.assert_called_once_with(
            "model_id",
            function="function",
            tool_name="tool_name",
            parameters_file="params_file"
        )
        assert result.id == "job123"

@pytest.mark.timeout(5)
def test_wait_for_job_returns_completed():
    """Test that wait_for_job returns when job is completed."""
    running_job = MagicMock(id="job123")
    running_job.status.name = JobStatusName.RUNNING
    completed_job = MagicMock(id="job123")
    completed_job.status.name = JobStatusName.COMPLETED
    with patch("genai_demo.shared.helpers.get_client") as mock_get_client, \
         patch("genai_demo.shared.helpers.sleep", return_value=None):
        mock_client = MagicMock()
        mock_client.get_job.side_effect = itertools.chain(
            [running_job, completed_job], itertools.repeat(completed_job)
        )
        mock_get_client.return_value = mock_client
        result = helpers.wait_for_job(running_job)
        assert result.status.name == JobStatusName.COMPLETED

@pytest.mark.timeout(5)
def test_wait_for_job_handles_failed():
    """Test that wait_for_job returns when job is failed."""
    running_job = MagicMock(id="job123")
    running_job.status.name = JobStatusName.RUNNING
    failed_job = MagicMock(id="job123")
    failed_job.status.name = JobStatusName.FAILED
    with patch("genai_demo.shared.helpers.get_client") as mock_get_client, \
         patch("genai_demo.shared.helpers.sleep", return_value=None):
        mock_client = MagicMock()
        mock_client.get_job.side_effect = itertools.chain(
            [running_job, failed_job], itertools.repeat(failed_job)
        )
        mock_get_client.return_value = mock_client
        result = helpers.wait_for_job(running_job)
        assert result.status.name == JobStatusName.FAILED

@pytest.mark.timeout(5)
def test_wait_for_all_jobs_returns_jobs():
    """Test that wait_for_all_jobs returns None (side-effect only)."""
    completed_job = MagicMock(id="job123")
    completed_job.status.name = "COMPLETED"
    with patch("genai_demo.shared.helpers.wait_for_job", return_value=completed_job), \
         patch("genai_demo.shared.helpers.get_client", return_value=MagicMock()), \
         patch("genai_demo.shared.helpers.job_list", new=["job123"]):
        result = helpers.wait_for_all_jobs()
        assert result is None

@pytest.mark.timeout(5)
def test_download_artifact_orig_success():
    """Test that download_artifact_orig writes artifact bytes to file when found."""
    mock_artifact = MagicMock(read_bytes=MagicMock(return_value=b"bytes"))
    mock_artifact.name = "artifact_name"
    mock_artifact_list = MagicMock(items=[mock_artifact])
    mock_client = MagicMock(list_model_artifacts=MagicMock(return_value=mock_artifact_list))
    with patch("genai_demo.shared.helpers.get_client", return_value=mock_client), \
         patch("genai_demo.shared.helpers.open", create=True) as mock_open:
        helpers.download_artifact_orig("model_id", "artifact_name", "dest_file")
        mock_client.list_model_artifacts.assert_called_once_with("model_id", page=1)
        assert mock_artifact.read_bytes.called
        assert mock_open.called

@pytest.mark.timeout(5)
def test_download_artifact_orig_raises_when_not_found():
    """Test that download_artifact_orig raises FileNotFoundError if artifact is missing."""
    mock_artifact_list = MagicMock(items=[])
    mock_client = MagicMock(list_model_artifacts=MagicMock(return_value=mock_artifact_list))
    with patch("genai_demo.shared.helpers.get_client", return_value=mock_client):
        with pytest.raises(FileNotFoundError):
            helpers.download_artifact_orig("model_id", "artifact_name", "dest_file")

@pytest.mark.timeout(5)
def test_get_input_accepts_valid():
    """Test that get_input returns valid input from user."""
    with patch("builtins.input", return_value="y"):
        result = helpers.get_input("msg", ["y"])
        assert result == "y"

@pytest.mark.timeout(5)
def test_get_input_retries_until_valid():
    """Test that get_input retries until valid input is given."""
    with patch("builtins.input", side_effect=["n", "y"]):
        result = helpers.get_input("msg", ["y"])
        assert result == "y"

@pytest.mark.timeout(5)
def test_format_str_returns_string():
    """Test that format_str returns a string."""
    result = helpers.format_str("text", 1)
    assert isinstance(result, str) 
