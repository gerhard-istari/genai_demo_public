import sys

from shared.helpers import get_client, wait_for_job, download_artifact
from shared.constants import CAMEO_MODEL_ID, REQ_FILE_NAME


def extract_requirements(client: Client):
  print('Starting Cameo model extraction ...')
  job = client.add_job(model_id = CAMEO_MODEL_ID,
                       function = '@istari:extract',
                       tool_name = 'dassault_cameo')
  print(f"Job submitted with ID: {job.id}")
  
  wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")

  print("Downloading requirements artifact ...")
  download_artifact(CAMEO_MODEL_ID,
                    REQ_FILE_NAME)
  print('Requirements artifact downloaded')


if __name__ == '__main__':
  client = get_client()
  extract_requirements(client)
