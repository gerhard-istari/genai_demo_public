import json
import re
from prettytable import PrettyTable
from enum import Enum, auto
from shared.helpers import format_str


class BoundType(Enum):
  RANGE = auto()
  LESS_THAN = auto()
  LESS_THAN_EQUAL = auto()
  GREATER_THAN = auto()
  GREATER_THAN_EQUAL = auto()
  EQUAL_TO = auto()


class Parameter():

  def __init__(self, param_str: str):
    self.value, self.units = self.parse_param_str(param_str)

  def get_value_str(self):
    return f"{self.value}{self.units}"

  def parse_param_str(self,
                      param_str: str) -> tuple[str, str]:
    m = re.match('^([\d.eE\-\+]+)(.*)',
                 param_str)
    if m is None:
      param_val = 0
      param_units = ''
    else:
      grps = m.groups(1)
      try:
        param_val = float(grps[0])
      except ValueError:
        param_val = 0.0
      param_units = grps[1] if len(grps) > 1 else ''

    return tuple([param_val,
                  param_units])


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
      case BoundType.EQUAL_TO:
        ret_val = val == self.get_
      case _:
        raise TypeError(f"Unrecognized bound type: {self.get_type()}")

    return ret_val

  def parse_bnd_str(self,
                    bnd_str: str):
    bnd_str = bnd_str.strip()
    m = re.search(r"^(?:\[)+\s*([^;]+)\s*;\s*([^\]]+)\s*(?:\])+$",
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

    m = re.search(r"^>(=?)\s*(.*)$",
                  bnd_str)
    if not m is None:
      if m.groups(1)[0] is None:
        self.type = BoundType.GREATER_THAN
      else:
        self.type = BoundType.GREATER_THAN_EQUAL
      self.lower = None
      self.upper = float(m.groups(1)[1])
      return

    m = re.search(r"^=\s*(.*)$",
                  bnd_str)
    if not m is None:
      val = float(m.groups(1)[0])
      self.lower = val
      self.upper = val
      return

  def get_nearest_passing_value(self,
                                val: float) -> float:
    if self.is_satisfied(val):
      ret_val = val
    else:
      match self.get_type():
        case BoundType.EQUAL_TO:
          ret_val = self.get_lower()
        case BoundType.LESS_THAN:
          ret_val = self.get_upper() - 2.0 * sys.float_info.epsilon
        case BoundType.LESS_THAN_EQUAL:
          ret_val = self.get_upper()
        case BoundType.GREATER_THAN:
          ret_val = self.get_lower() + 2.0 * sys.float_info.epsilon
        case BoundType.GREATER_THAN_EQUAL:
          ret_val = self.get_lower()
        case BoundType.RANGE:
          ret_val = self.get_lower() if abs(val - self.get_lower()) < abs(val - self.get_upper()) else self.get_upper()

    return ret_val


def get_column_header_color() -> int:
  return 34


def find_param_reqs(req_file: str,
                    param_file: str) -> list[tuple[dict[str, object], dict[str, object]]]:
  prs = []

  with open(req_file, 'r', encoding='Windows-1252') as fin:
    reqs_obj = json.load(fin)

  with open(param_file, 'r') as fin:
    params_obj = json.load(fin)

  for param_obj in params_obj:
    params = param_obj['parameters']
    if not params is None:
      for param in params:
        param_name = param['name'].split('\\')[-1].strip()
        param_srch_str = f"{param_name}"

        for req_obj in reqs_obj:
          req_name = req_obj['qualified_name'].strip()
          if not req_name is None and req_name.endswith(param_srch_str):
            prs.append((param, req_obj))

  return prs


def get_failing_params(param_reqs: list[tuple[dict[str, object], dict[str, object]]]) -> list[tuple[dict[str, object], dict[str, object]]]:
  fail_param_reqs = []
  for param_req in param_reqs:
    param_obj, req_obj = param_req
    if not check_requirement(param_obj, req_obj):
      fail_param_reqs.append(param_req)

  return fail_param_reqs

  
def check_requirement(param_obj: dict[str, object],
                      req_obj: dict[str, object]) -> bool:
  param_str = param_obj['value']
  bnd = Bounds(req_obj['bounds'])
  param = Parameter(param_str)

  return bnd.is_satisfied(param.value)


def print_summary(param_reqs: list[tuple[dict[str, object], dict[str, object]]]):
  print('Validating CAD parameters against requirements ...')
  
  tab = PrettyTable()
  header_color = get_column_header_color();
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
    param, req = param_req
    param_name = param['name']
    param_val = param['value']
    req_bnds = req['bounds']
    
    req_qual_name = req['qualified_name']
    if check_requirement(param, req):
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


def fix_failing_params(param_reqs: list[tuple[dict[str, object], dict[str, object]]]) -> list[dict[str, str]]:
  pt = PrettyTable()
  header_color = get_column_header_color()
  param_col_header = format_str('CAD Parameter',
                                header_color, 1)
  val_col_header = format_str('New Value',
                              header_color, 1)
  pt.field_names = [param_col_header,
                    val_col_header]
  new_params = []
  for param_req in param_reqs:
    param_obj, req_obj = param_req
    bnd = Bounds(req_obj['bounds'])
    param = Parameter(param_obj['value'])
    param.value = bnd.get_nearest_passing_value(param.value)
    new_param = {}
    new_param['name'] = param_obj['name']
    new_param['value'] = param.get_value_str()
    new_param['units'] = param_obj['units']
    new_params.append(new_param)
    pt.add_row([param_obj['name'],
                param.get_value_str()])

  print(pt)
  return new_params


if __name__ == '__main__':
  validate_requirements()

