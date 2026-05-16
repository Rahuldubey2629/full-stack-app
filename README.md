# Azure Learning Lab

This repository is a practical full stack app for learning Azure the way it is used in real delivery work.

It gives you a Django REST API with health endpoints and task CRUD backed by PostgreSQL (or SQLite locally). The Azure side is intentionally left for you to do yourself so you can practice the real workflow.

## What is in here

- Django REST API with task CRUD and health checks.
- PostgreSQL-ready configuration for Azure.
- Azure DevOps pipeline starter in [azure-pipelines.yml](azure-pipelines.yml).
- Azure learning notes in [docs/azure-learning-path.md](docs/azure-learning-path.md).
- Example env values in [.env.example](.env.example).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver 0.0.0.0:8000
```

## Build check

```bash
python backend/manage.py check
python backend/manage.py collectstatic --noinput
```

## Azure path to practice yourself

Start with a resource group, App Service plan, Linux App Service, Key Vault, and APIM. Then wire the app to App Service, replace secrets with Key Vault references, and import the OpenAPI document into APIM.

The full step-by-step path is in [docs/azure-learning-path.md](docs/azure-learning-path.md).

## Useful endpoints

- `/api/health/live`
- `/api/health/ready`
- `/api/config`
- `/api/tasks`

## Good KT questions

- Which secrets are stored in Key Vault and which are still pipeline variables?
- Which APIM policies are mandatory for the real project?
- Is the App Service deployed from source, zip, or container?
- Which Azure Policy assignments are required in the subscription?
- How are logs and traces reviewed during an incident?
