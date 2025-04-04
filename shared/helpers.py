from time import sleep

from istari_digital_client import Client, Configuration, Job
from istari_digital_client.openapi_client.models.job_status_name import JobStatusName


def get_client():
  registry_url = 'https://fileservice-v2.dev2.istari.app/'
  registry_auth_token = 'iM8CeWDous_KE8dsi_4-goI8oMMig2Gl_64_0gCMOYkZ_NAu0eEgsDGSvP69cIneLIPYR1g'
  demo_reg_url = 'https://fileservice-v2.demo.istari.app/'
  demo_reg_auth_token = 'LF-6ZetnVKHLH0zG-CuSWWcyav0gWv7o39ab51gtXyA1qjerMfpcWuRDnxdZnEFX4lrt8Ew'
  configuration = Configuration(
      registry_url=demo_reg_url,
      registry_auth_token=demo_reg_auth_token,
  )

  return Client(config = configuration)


def wait_for_job(job) -> Job:
  client = get_client()
  empty_str = ' ' * 64
  while not job.status.name in [JobStatusName.COMPLETED, 
                                JobStatusName.FAILED]:
    sleep(1)
    job = client.get_job(job.id)
    print(empty_str, end="\r")
    job_stat = format_str(job.status.name, 1)
    print(f"Job Status: {job_stat}", end="\r")

  print(empty_str, end="\r")
  return job


def download_artifact(model_id: str,
                      artifact_name: str,
                      dest_file: str = None) -> str:
  client = get_client()
  art = None
  pg_idx = 1
  while True:
    art_list = client.list_model_artifacts(model_id,
                                           page = pg_idx)
    art_items = art_list.items
    if len(art_items) == 0:
      break
    
    for itm in art_items:
      if itm.name == artifact_name:
        art = itm
        break

    if art is not None: break
    pg_idx += 1

  if art is None:
    raise FileNotFoundError(f"Artifact not found: {artifact_name}")
  else:
    if dest_file is None:
      dest_file = artifact_name
    with open(dest_file, 'wb') as fout:
      fout.write(art.read_bytes())


def get_input(msg: str,
              allowed_resps: list[str] = None) -> str:
  while True:
    ans = input(msg).lower()
    if allowed_resps is None or ans in allowed_resps:
      break
    else:
      print('Invalid response')

  return ans


def format_str(text: str,
               color: int,
               effect1: int = -1,
               effect2: int = -1):
  FMT_PREFIX = '\033['
  fmt_str = f"{FMT_PREFIX}{color}"
  if effect1 >= 0:
    fmt_str += f";{effect1}"
  if effect2 >= 0:
    fmt_str += f";{effect2}"

  return f"{fmt_str}m{text}{FMT_PREFIX}0m"
