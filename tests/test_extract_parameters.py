from unittest.mock import patch, MagicMock
import genai_demo.components.extract_parameters as ep

def test_extract_parameters_coverage():
    with patch("genai_demo.components.extract_parameters.submit_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_parameters.wait_for_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_parameters.download_artifact", return_value=None), \
         patch("genai_demo.components.extract_parameters.print"):
        ep.extract_parameters(MagicMock(), "cad_mod_id", "param_file_name") 
