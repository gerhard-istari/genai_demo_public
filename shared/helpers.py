from istari import Client, Configuration
from istari.openapi_client.models.job_status import JobStatus


def get_client():
  registry_url = 'https://fileservice-v2.dev2.istari.app/'
  registry_auth_token = 'iM8CeWDous_KE8dsi_4-goI8oMMig2Gl_64_0gCMOYkZ_NAu0eEgsDGSvP69cIneLIPYR1g'
  configuration = Configuration(
      registry_url=registry_url,
      registry_auth_token=registry_auth_token,
  )

  return Client(config = configuration)


def wait_for_job(job):
  while job.status.name in {JobStatus.Name.COMPLETED, JobStatus.Name.FAILED}:
    sleep(1)
