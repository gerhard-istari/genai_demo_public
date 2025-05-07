from unittest.mock import patch, MagicMock
import genai_demo.components.extract_requirements as er

def test_extract_requirements_calls_sdk_and_downloads_artifact():
    """Test that extract_requirements submits a job, waits for it, and downloads the artifact."""
    with patch("genai_demo.components.extract_requirements.submit_job") as mock_submit_job, \
         patch("genai_demo.components.extract_requirements.wait_for_job") as mock_wait_for_job, \
         patch("genai_demo.components.extract_requirements.download_artifact") as mock_download_artifact, \
         patch("genai_demo.components.extract_requirements.CAMEO_TOOL_NAME", "mock_tool"), \
         patch("genai_demo.components.extract_requirements.print"):
        client = MagicMock()
        cam_mod_id = "cam_mod_id"
        req_file_name = "req_file_name"
        er.extract_requirements(client, cam_mod_id, req_file_name)
        mock_submit_job.assert_called_once_with(
            model_id=cam_mod_id,
            function='@istari:extract',
            tool_name='mock_tool'
        )
        mock_wait_for_job.assert_called_once()
        mock_download_artifact.assert_called_once_with(cam_mod_id, req_file_name)

def test_extract_requirements_coverage():
    with patch("genai_demo.components.extract_requirements.submit_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_requirements.wait_for_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_requirements.download_artifact", return_value=None), \
         patch("genai_demo.components.extract_requirements.print"):
        er.extract_requirements(MagicMock(), "cam_mod_id", "req_file_name") 
