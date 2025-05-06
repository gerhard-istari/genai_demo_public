import pytest
from unittest.mock import patch, MagicMock

from genai_demo.components.extract_parameters import extract_parameters

def test_extract_parameters_calls_helpers():
    # Create a fake client and job
    fake_client = MagicMock()
    fake_job = MagicMock()
    fake_job.id = "job123"
    fake_job.status.name = "SUCCESS"

    with patch("src.components.extract_parameters.submit_job", return_value=fake_job) as mock_submit_job, \
         patch("src.components.extract_parameters.wait_for_job", return_value=fake_job) as mock_wait_for_job, \
         patch("src.components.extract_parameters.download_artifact") as mock_download_artifact, \
         patch("src.components.extract_parameters.MOD_TOOL_NAME", "mock_tool"):

        extract_parameters(fake_client, "cad_mod_id", "param_file_name")

        mock_submit_job.assert_called_once_with(
            model_id="cad_mod_id",
            function='@istari:extract_parameters',
            tool_name="mock_tool"
        )
        mock_wait_for_job.assert_called_once_with(fake_job)
        mock_download_artifact.assert_called_once_with("cad_mod_id", "param_file_name")
