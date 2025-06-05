from istari_digital_client import Client

from shared.helpers import get_client, submit_job, wait_for_job, download_artifact
from shared.constants import CAMEO_MODEL_ID, REQ_FILE_NAME, CAMEO_TOOL_NAME


def extract_requirements(client: Client,
                         cam_mod_id: str,
                         req_file_name: str):
  print('Submitting job to extract Cameo model requirements ...')
  job = submit_job(model_id = cam_mod_id,
                   function = '@istari:extract',
                   tool_name = CAMEO_TOOL_NAME,
                   tool_ver = CAMEO_VERSION)
  print(f"Job submitted with ID: {job.id}")
  
  wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")

  print("Downloading requirements artifact ...")
  download_artifact(cam_mod_id,
                    req_file_name)
  print('Requirements artifact downloaded')


if __name__ == '__main__':
  client = get_client()
  extract_requirements(client,
                       CAMEO_MODEL_ID,
                       REQ_FILE_NAME)
