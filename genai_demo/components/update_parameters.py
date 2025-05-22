import json
import os

from istari_digital_client import Client
from ..shared.helpers import submit_job, wait_for_job
from ..shared.constants import CAD_TOOL_NAME


def update_parameters(client: Client,
                      cad_mod_id: str,
                      update_param_file_name: str):
  print('Submitting job to update 3DX model parameters ...')

  with open(update_param_file_name, 'r') as fin:
    update_params = json.load(fin)

  job = submit_job(model_id = cad_mod_id,
                   function = '@istari:update_parameters',
                   tool_name = CAD_TOOL_NAME,
                   params_file = update_param_file_name)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  print(f"Job Complete [{job.status.name}]")

  print('Updating CAD model version ...')
  mod = client.get_model(cad_mod_id)
  with open(mod.name, 'wb') as fout:
    fout.write(mod.file.read_bytes())
  client.update_model(cad_mod_id,
                      mod.name)
  os.remove(mod.name)


if __name__ == '__main__':
  client = get_client()
  update_parameters(client)
