from time import sleep
from istari_digital_client import Client

from shared.helpers import get_client, wait_for_job, download_artifact
from shared.constants import CAD_MODEL_ID, PARAM_FILE_NAME, MOD_TOOL_NAME


def extract_parameters(client: Client):
  print('Starting 3DX model extraction ...')
  job = client.add_job(model_id = CAD_MODEL_ID,
                       function = '@istari:extract_parameters',
                       tool_name = MOD_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")
  
  sleep(5)
  download_artifact(CAD_MODEL_ID,
                    PARAM_FILE_NAME)


if __name__ == '__main__':
  client = get_client()
  extract_parameters(client)
