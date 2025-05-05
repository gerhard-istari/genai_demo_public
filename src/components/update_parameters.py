import json

from istari_digital_client import Client
from shared.helpers import wait_for_job
from shared.constants import CAD_MODEL_ID, UPDATE_PARAM_FILE_NAME, MOD_TOOL_NAME


def update_parameters(client: Client,
                      cad_mod_id: str,
                      update_param_file_name: str):
  print('Submitting job to update 3DX model parameters ...')

  with open(UPDATE_PARAM_FILE_NAME, 'r') as fin:
    update_params = json.load(fin)

  job = client.add_job(model_id = cad_mod_id,
                       function = '@istari:update_parameters',
                       tool_name = MOD_TOOL_NAME,
                       parameters_file = update_param_file_name)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")


if __name__ == '__main__':
  client = get_client()
  update_parameters(client)
