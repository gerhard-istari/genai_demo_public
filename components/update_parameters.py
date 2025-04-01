import json

from istari_digital_client import Client
from shared.helpers import wait_for_job
from shared.constants import CAD_MODEL_ID, UPDATE_PARAM_FILE_NAME, MOD_TOOL_NAME


def update_parameters(client: Client):
  print('Updating 3DX model parameters')

  #with open(UPDATE_PARAM_FILE_NAME, 'r') as fin:
  #  update_params = json.load(fin)

  job = client.add_job(model_id = CAD_MODEL_ID,
                       function = '@istari:update_parameters',
                       tool_name = MOD_TOOL_NAME,
                       parameters_file = UPDATE_PARAM_FILE_NAME)
  job = wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")


if __name__ == '__main__':
  client = get_client()
  update_parameters(client)
