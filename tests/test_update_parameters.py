from unittest.mock import patch, MagicMock
import pytest
import genai_demo.components.update_parameters as up
import os

@pytest.mark.timeout(5)
def test_update_parameters_updates_model_on_success():
    """Test that update_parameters submits a job, waits for it, updates the model, and cleans up."""
    with patch("genai_demo.components.update_parameters.submit_job") as mock_submit_job, \
         patch("genai_demo.components.update_parameters.wait_for_job") as mock_wait_for_job, \
         patch("genai_demo.components.update_parameters.open"), \
         patch("genai_demo.components.update_parameters.json.load", return_value={}), \
         patch("genai_demo.components.update_parameters.print"), \
         patch("genai_demo.components.update_parameters.CAD_TOOL_NAME", "mock_tool"), \
         patch("os.remove") as mock_remove:
        client = MagicMock()
        client.get_model = MagicMock(return_value=MagicMock(file=MagicMock(read_bytes=MagicMock(return_value=b"")), name="model_file_name"))
        client.update_model = MagicMock()
        cad_mod_id = "cad_mod_id"
        update_param_file_name = "update_parameters.json"
        up.update_parameters(client, cad_mod_id, update_param_file_name)
        mock_submit_job.assert_called_once_with(
            model_id=cad_mod_id,
            function='@istari:update_parameters',
            tool_name='mock_tool',
            params_file=update_param_file_name
        )
        mock_wait_for_job.assert_called_once()
        client.get_model.assert_called_once_with(cad_mod_id)
        client.update_model.assert_called_once()
        mock_remove.assert_called_once()

@pytest.mark.timeout(5)
def test_update_parameters_coverage():
    with patch("genai_demo.components.update_parameters.submit_job", return_value=MagicMock(status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.update_parameters.wait_for_job", return_value=MagicMock(status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.update_parameters.open"), \
         patch("genai_demo.components.update_parameters.json.load", return_value={}), \
         patch("genai_demo.components.update_parameters.print"), \
         patch("genai_demo.components.update_parameters.Client.get_model", return_value=MagicMock(file=MagicMock(read_bytes=MagicMock(return_value=b"")), name="model_file_name")), \
         patch("genai_demo.components.update_parameters.Client.update_model", return_value=None), \
         patch("os.remove", return_value=None):
        up.update_parameters(MagicMock(), "", "update_parameters.json") 
