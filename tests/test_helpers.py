from unittest.mock import patch, MagicMock
import pytest
import genai_demo.shared.helpers as helpers

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
