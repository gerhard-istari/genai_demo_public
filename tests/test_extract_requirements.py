from unittest.mock import patch, MagicMock
import genai_demo.components.extract_requirements as er

def test_extract_requirements_coverage():
    with patch("genai_demo.components.extract_requirements.submit_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_requirements.wait_for_job", return_value=MagicMock(id="job123", status=MagicMock(name="COMPLETED"))), \
         patch("genai_demo.components.extract_requirements.download_artifact", return_value=None), \
         patch("genai_demo.components.extract_requirements.print"):
        er.extract_requirements(MagicMock(), "cam_mod_id", "req_file_name") 
