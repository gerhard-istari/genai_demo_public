import argparse
import json
import re
import sys

from istari_digital_client import Client
from components.extract_requirements import extract_requirements
from components.extract_parameters import extract_parameters
from components.update_parameters import update_parameters
from components.validate_requirements import print_summary, find_param_reqs, check_requirement, get_failing_params, fix_failing_params
from shared.helpers import get_client, format_str, get_input, wait_for_new_version, download_artifact, get_latest_revision, wait_for_all_jobs
from shared.constants import *


#################
### Functions ###
#################
def automated(client: Client):
  cad_mod_id = CAD_MODEL_ID
  cam_mod_id = CAMEO_MODEL_ID
  CAD_MOD_FILE = 'cad_model.dassault_3dexperience_metadata'

  while True:
    #cam_rev = wait_for_new_version(CAMEO_MODEL_ID)

    max_tries = 2
    for try_idx in range(max_tries):
      print('Retrieving system requirements ...')
      get_artifact(client,
                   cam_mod_id,
                   REQ_FILE_NAME,
                   extract_requirements)
      print('Retrieving CAD parameters ...')
      get_artifact(client,
                   cad_mod_id,
                   PARAM_FILE_NAME,
                   extract_parameters)

      param_reqs = find_param_reqs(REQ_FILE_NAME,
                                   PARAM_FILE_NAME)
      print_summary(param_reqs)
      os.remove(REQ_FILE_NAME)
      os.remove(PARAM_FILE_NAME)

      fail_param_reqs = get_failing_params(param_reqs)
      fail_count = len(fail_param_reqs)
      if fail_count == 0:
        msg = 'CAD Parameters satisfy all associated requirements'
        print(f"{format_str(msg, GREEN_COLOR, BOLD_FORMAT)}")
        break
      else:
        msg = f"{fail_count} failed requirement(s) found"
        print(f"{format_str(msg, RED_COLOR, BOLD_FORMAT)}")
        print('Calculating new values for failing parameters ...')
        new_params = fix_failing_params(fail_param_reqs)

        print('Pushing updated parameter values to CAD model ...')
        save_params_to_input_json(new_params,
                                  UPDATE_PARAM_FILE_NAME)
        update_parameters(client,
                          cad_mod_id,
                          UPDATE_PARAM_FILE_NAME)

        # TODO: Ideally, this will utilize model versions, but there are
        # complications with how to access model version-specific artifacts.
        # For now, upload new model.
        print('Creating new version of CAD model ...')
        cad_mod_id = create_model_copy(cad_model_id)


def interactive(client: Client):
  cad_mod_id = CAD_MODEL_ID

  print('Retrieving system requirements ...')
  get_artifact(client,
               CAMEO_MODEL_ID,
               REQ_FILE_NAME,
               extract_requirements)
  
  while True:
    print('Retrieving CAD parameters ...')
    get_artifact(client,
                 cad_mod_id,
                 PARAM_FILE_NAME,
                 extract_parameters)

    param_reqs = find_param_reqs(REQ_FILE_NAME,
                                 PARAM_FILE_NAME)
    print_summary(param_reqs)
  
    fail_param_reqs = []
    for param_req in param_reqs:
      param_obj, req_obj = param_req
      if not check_requirement(param_obj, req_obj):
        fail_param_reqs.append(param_req)
  
    fail_count = len(fail_param_reqs)
    if fail_count == 0:
      msg = "CAD Parameters satisfy all associated requirements"
      print(f"{format_str(msg, 32, 1)}")
      break
  
    msg = f"{fail_count} failed requirement(s) found"
    print(f"{format_str(msg, 31, 1)}")
  
    if fail_count > 0:
      ans = get_input('Update failing CAD Parameter values (y,[n])? ',
                      ['y', 'n', 'yes', 'no', ''])
      update_params = []
      if ans.startswith('y'):
        for param_req in fail_param_reqs:
          param_obj, req_obj = param_req
          param_obj_name = param_obj['name']
          bold_param_name = format_str(param_obj_name, 4)
          while True:
            req_bnds = req_obj['bounds']
            param_val = param_obj['value'] = input(f"Enter new value for parameter {bold_param_name} ({req_bnds}): ").strip()
            if re.search(r"[a-z,A-Z]+$", param_val) == None:
              err_msg = format_str('No units specified', 
                                   RED_COLOR)
              print(f"{err_msg}")
            elif check_requirement(param_obj, req_obj):
              update_params.append(param_obj)
              break
            else:
              err_msg = format_str('Value does not satisfy requirement', 
                                   RED_COLOR)
              print(f"{err_msg}: ({req_bnds})")
  
      if len(update_params) > 0:
        save_params_to_input_json(update_params,
                                  UPDATE_PARAM_FILE_NAME)
        update_parameters(client,
                          CAD_MODEL_ID,
                          UPDATE_PARAM_FILE_NAME)
        cad_mod_id = create_model_copy(cad_mod_id)
      else: break


def create_model_copy(mod_id: str) -> str:
  mod = client.get_model(mod_id)
  with open(mod.name, 'wb') as fout:
    fout.write(mod.file.read_bytes())
  new_mod_id = client.add_model(mod.name).id
  os.remove(mod.name)
  return new_mod_id


def save_params_to_input_json(param_objs: list[dict[str, str]],
                              json_file: str):
  json_obj = {}
  json_obj['parameters'] = update_params = {}
  for param_obj in param_objs:
    update_params[param_obj['name']] = param_obj['value']

  with open(json_file, 'w') as fout:
    json.dump(json_obj, fout)


def get_artifact(client: Client,
                 mod_id: str,
                 art_file_name: str,
                 extract_function):
  print('Searching for artifact ...')
  #mod_id = get_latest_revision(mod_id)
  try:
    download_artifact(mod_id,
                      art_file_name,
                      art_file_name)
  except FileNotFoundError:
    msg = format_str('Artifact not found',
                     RED_COLOR)
    print(f"{msg}. Extracting ...")
    extract_function(client,
                     mod_id,
                     art_file_name)
  msg = format_str('Artifact downloaded successfully',
                   GREEN_COLOR)
  print(msg)


### MAIN ###
if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='GenAI Demo')
  parser.add_argument('--poll',
                      action='store_true')
  args = parser.parse_args()

  client = get_client()

  try:
    if args.poll:
      automated(client)
    else:
      interactive(client)
  except KeyboardInterrupt:
    print("\nWaiting for any executing jobs to complete ...")
    wait_for_all_jobs()
    print('Shutting down')
    sys.exit(0)

