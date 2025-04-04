import json

from components.extract_requirements import extract_requirements
from components.extract_parameters import extract_parameters
from components.update_parameters import update_parameters
from components.validate_requirements import print_summary, find_param_reqs, check_requirement
from shared.helpers import get_client, format_str, get_input
from shared.constants import REQ_FILE_NAME, PARAM_FILE_NAME, UPDATE_PARAM_FILE_NAME


client = get_client()

extract_requirements(client)

while True:
  extract_parameters(client)

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
    update_params = {}
    if ans.startswith('y'):
      params_obj = {}
      params_obj['parameters'] = update_params
      for param_req in fail_param_reqs:
        param_obj, req_obj = param_req
        param_obj_name = param_obj['name']
        bold_param_name = format_str(param_obj_name, 4)
        while True:
          req_bnds = req_obj['bounds']
          param_obj['value'] = input(f"Enter new value for parameter {bold_param_name} ({req_bnds}): ")
          if check_requirement(param_obj, req_obj):
            update_params[param_obj_name] = param_obj['value']
            break
          else:
            err_msg = format_str('Value does not satisfy requirement', 31)
            print(f"{err_msg}: ({req_bnds})")

    if len(update_params) > 0:
      with open(UPDATE_PARAM_FILE_NAME, 'w') as fout:
        json.dump(params_obj, fout)

      update_parameters(client)
    else: break
