import json
import re
from prettytable import PrettyTable
from enum import Enum, auto
from shared.helpers import format_str
from shared.constants import REQ_FILE_NAME, PARAM_FILE_NAME


class BoundType(Enum):
  RANGE = auto()
  LESS_THAN = auto()
  LESS_THAN_EQUAL = auto()
  GREATER_THAN = auto()
  GREATER_THAN_EQUAL = auto()


class Bounds():
  
  def __init__(self, bnd_str: str):
    self.lower = None
    self.upper = None
    self.type = None
    self.parse_bnd_str(bnd_str)

  def get_lower(self) -> float:
    return self.lower

  def get_upper(self) -> float:
    return self.upper

  def get_type(self) -> BoundType:
    return self.type
    
  def is_satisfied(self, 
                   val: float) -> bool:
    ret_val = False
    match self.get_type():
      case BoundType.RANGE:
        ret_val = val >= self.get_lower() and val <= self.get_upper()
      case BoundType.LESS_THAN:
        ret_val = val < self.get_upper()
      case BoundType.LESS_THAN_EQUAL:
        ret_val = val <= self.get_upper()
      case BoundType.GREATER_THAN:
        ret_val = val > self.get_lower()
      case BoundType.GREATER_THAN_EQUAL:
        ret_val = val >= self.get_lower()
      case _:
        raise TypeError(f"Unrecognized bound type: {self.get_type()}")

    return ret_val

  def parse_bnd_str(self,
                    bnd_str: str):
    bnd_str = bnd_str.strip()
    m = re.search(r"^\[\s*([^;]+)\s*;\s*([^;]+)\s*\]$",
                  bnd_str)
    if not m is None:
      self.type = BoundType.RANGE
      self.lower = float(m.groups(1)[0])
      self.upper = float(m.groups(1)[1])
      return

    m = re.search(r"^<(=?)\s*(.*)$",
                  bnd_str)
    if not m is None:
      if m.groups(1)[0] is None:
        self.type = BoundType.LESS_THAN
      else:
        self.type = BoundType.LESS_THAN_EQUAL
      self.lower = None
      self.upper = float(m.groups(1)[1])
      return


def find_param_reqs(req_file: str,
                    param_file: str) -> list[tuple[dict[str, object], dict[str, object]]]:
  prs = []

  with open(req_file, 'r', encoding='Windows-1252') as fin:
    reqs_obj = json.load(fin)

  with open(param_file, 'r') as fin:
    params_obj = json.load(fin)

  for param_obj in params_obj:
    for param in param_obj['parameters']:
      param_name = param['name'].split('\\')[-1]
      param_srch_str = f"::{param_name}"

      for req_obj in reqs_obj:
        req_name = req_obj['qualified_name']
        if req_name.endswith(param_srch_str):
          prs.append((param, req_obj))

  return prs


def check_requirement(param_obj: dict[str, object],
                      req_obj: dict[str, object]) -> bool:
  param_val = param_obj['value']
  bnd = Bounds(req_obj['bounds'])
  m = re.match('^([\d.eE\-\+]+)',
               param_val)
  if (m is None): return False

  try:
    param_val = float(m.groups(1)[0])
    return bnd.is_satisfied(float(param_val))
  except ValueError:
    return False


def print_summary(param_reqs: list[tuple[dict[str, object], dict[str, object]]] = None):
  print('Validating CAD parameters against requirements ...')
  
  if param_reqs is None:
    param_reqs = find_param_reqs(REQ_FILE_NAME,
                                 PARAM_FILE_NAME)

  tab = PrettyTable()
  header_color = 34
  req_col_header = format_str('Requirement',
                              header_color, 1)
  param_col_header = format_str('CAD Parameter',
                                header_color, 1)
  bounds_col_header = format_str('Bounds',
                                 header_color, 1)
  param_val_col_header = format_str('Parameter Value',
                                    header_color, 1)
  tab.field_names = [req_col_header,
                     param_col_header, 
                     bounds_col_header,
                     param_val_col_header]
  # Search for relevant requirements for 3DX parameters
  for param_req in param_reqs:
    param, req_obj = param_req
    param_name = param['name']
    param_val = param['value']
    req_bnds = req_obj['bounds']
    
    req_qual_name = req_obj['qualified_name']
    if check_requirement(param, req_obj):
      req_str = format_str(req_qual_name, 32)
    else:
      req_str = format_str(req_qual_name, 31)

    tab.add_row([req_str,
                 param_name,
                 req_bnds,
                 param_val])

  tab.align = 'l'
  print(tab)

  # TODO: How to deal with units?

  #job = client.add_job(model_id = CAD_MODEL_ID,
  #                     function = '@istari:extract_parameters',
  #                     tool_name = 'dassault_3dexperience')
  #print(f"Job submitted with ID: {job.id}")

  #wait_for_job(job)
  #print(f"Job Complete [{job.status.name}]")


if __name__ == '__main__':
  validate_requirements()

