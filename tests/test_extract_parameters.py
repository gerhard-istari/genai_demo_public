from unittest.mock import patch, MagicMock
import genai_demo.components.extract_parameters as ep

def test_extract_parameters_calls_sdk_and_downloads_artifact():
    """Test that extract_parameters submits a job, waits for it, and downloads the artifact."""
    with patch("genai_demo.components.extract_parameters.submit_job") as mock_submit_job, \
         patch("genai_demo.components.extract_parameters.wait_for_job") as mock_wait_for_job, \
         patch("genai_demo.components.extract_parameters.download_artifact") as mock_download_artifact, \
         patch("genai_demo.components.extract_parameters.CAD_TOOL_NAME", "mock_tool"), \
         patch("genai_demo.components.extract_parameters.print"):
        client = MagicMock()
        cad_mod_id = "cad_mod_id"
        param_file_name = "param_file_name"
        ep.extract_parameters(client, cad_mod_id, param_file_name)
        mock_submit_job.assert_called_once_with(
            model_id=cad_mod_id,
            function='@istari:extract_parameters',
            tool_name='mock_tool',
            params_file='input.json'
        )
        mock_wait_for_job.assert_called_once()
        mock_download_artifact.assert_called_once_with(cad_mod_id, param_file_name)

def test_extract_parameters_coverage():
    with patch("genai_demo.components.extract_parameters.submit_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_parameters.wait_for_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_parameters.download_artifact", return_value=None), \
         patch("genai_demo.components.extract_parameters.print"):
        ep.extract_parameters(MagicMock(), "cad_mod_id", "param_file_name") 
