_debug_enabled = False

def set_debug(enabled: bool):
  global _debug_enabled
  _debug_enabled = enabled

def debug_log(msg: str):
  if _debug_enabled:
    print(f"[DEBUG] {msg}") 
