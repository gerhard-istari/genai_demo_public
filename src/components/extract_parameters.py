import os

from time import sleep
from istari_digital_client import Client

from shared.helpers import get_client, submit_job, wait_for_job, download_artifact
from shared.constants import CAD_MODEL_ID, PARAM_FILE_NAME, CAD_TOOL_NAME


def extract_parameters(client: Client,
                       cad_mod_id,
                       param_file_name: str):
  print('Submitting job to extract 3DX model parameters ...')

  input_file = 'input.json'
  with open(input_file, 'w') as fout:
    fout.write('{"full_extract": false}')

  job = submit_job(model_id = cad_mod_id,
                   function = '@istari:extract_parameters',
                   tool_name = CAD_TOOL_NAME,
                   params_file = input_file)
  print(f"Job submitted with ID: {job.id}")
  os.remove(input_file)

  job = wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")
  
  sleep(5)
  download_artifact(cad_mod_id,
                    param_file_name)


if __name__ == '__main__':
  client = get_client()
  extract_parameters(client,
                     CAD_MODEL_ID,
                     PARAM_FILE_NAME)
