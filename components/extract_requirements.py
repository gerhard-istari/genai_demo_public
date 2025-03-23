import sys
from istari import Client, Configuration

sys.path.insert(0, '.')
from shared.helpers import get_client
from shared.constants import CAMEO_MODEL_ID, REQ_FILE_NAME


client = get_client()

#print('Starting Cameo model extraction ...')
#job = client.add_job(model_id = CAMEO_MODEL_ID,
#                     function = '@istari:extract',
#                     tool_name = 'dassault_cameo')
#print(f"Job submitted with ID: {job.id}")
#
#wait_for_job(job)
#print(f"Job Complete [{job.status.name}]")

print("Searching for requirements artifact ...")
req_art = None
pg_idx = 1
while True:
  art_list = client.list_model_artifacts(CAMEO_MODEL_ID,
                                         page = pg_idx)
  art_items = art_list.items
  if len(art_items) == 0:
    break

  for itm in art_items:
    if itm.name == REQ_FILE_NAME:
      req_art = itm
      break

  if req_art is not None: break
  pg_idx += 1

if req_art is None:
  raise FileNotFoundError('Requirements artifact not found')
else:
  print('Requirements artifact found. Downloading ...')
  with open(REQ_FILE_NAME, 'wb') as fout:
    fout.write(req_art.read_bytes())
  print('Requirements artifact downloaded')
