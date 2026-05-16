# Azure Learning Path (Django + PostgreSQL)

This repo is designed to help you learn Azure with a real Django app instead of a toy sample.

## What this app gives you

- Django REST API with task tracking endpoints.
- PostgreSQL-ready configuration for App Service.
- A single deployable Django app that can run on Azure App Service.
- A clean place to insert Key Vault references for secrets.
- An Azure DevOps pipeline starter you can adapt.

## Suggested Azure topology

- Azure DevOps pipeline builds and validates the app.
- Azure App Service hosts the Django API.
- Azure API Management fronts the API when you want to learn gateway behavior.
- Azure Key Vault stores secrets and is referenced from App Service settings.
- Azure Policy enforces the shape of your resource group and App Service resources.

## Hands-on order I recommend

Do the services in this order so each step teaches the next one:

1. Run the app locally and understand the API contract.
2. Create the Azure resources manually in the portal.
3. Set up Azure DevOps service connection and pipeline.
4. Deploy to App Service.
5. Put Key Vault references in App Service settings.
6. Import the API into APIM.
7. Assign Azure Policy and test a rule that blocks bad config.

## Azure portal checklist

### Resource group

- Create one resource group for the whole lab.
- Add tags like `env=dev`, `owner=you`, and `project=azure-learning-lab`.

### App Service plan and web app

- Create a Linux App Service plan.
- Create a Linux Web App.
- Set the runtime stack to Python 3.12.
- Turn on HTTPS only.
- Turn on managed identity.
- Turn on Application Insights.

After deployment, add these app settings:

- `DJANGO_DEBUG=false`
- `DJANGO_ALLOWED_HOSTS=<your-app-service-host>`
- `DJANGO_SECRET_KEY=<secure-random-string>`
- `APP_NAME=Azure Learning Lab`
- `APP_MESSAGE=Practical Azure demo for App Service, APIM, Key Vault, and DevOps.`
- `DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>`

### Key Vault

- Create a Key Vault in the same region.
- Add a secret such as `APP_SECRET`.
- Grant the App Service managed identity permission to read secrets.
- Use a Key Vault reference in the App Service setting instead of the raw secret value.

### API Management

- Create APIM in the same region or a region close enough for the lab.
- Import the API endpoints from the deployed app.
- Start with a basic API and a subscription requirement.
- Add one simple policy like rate limiting or a header transform.

### Azure Policy

- Assign a policy that requires tags.
- Assign a policy that restricts allowed regions.
- Assign a policy that requires HTTPS on App Service.

## Azure DevOps setup

### 1. Create the service connection

In Azure DevOps, create a service connection to Azure using a service principal or workload identity federation.

What to capture:

- Service connection name.
- Subscription or management group scope.
- Target resource group if you want to lock it down later.

### 2. Create the pipeline

Point a new YAML pipeline at [azure-pipelines.yml](../azure-pipelines.yml).

Replace these values before running it:

- `azureServiceConnection`
- `webAppName`

### 3. Run build only first

Before enabling deploy, run the Build stage once.

This verifies:

- dependency install
- Django system check
- static asset collection

### 4. Enable deployment

Once build is green, let the Deploy stage run.

If deployment fails, check these first:

- the App Service name is correct
- the service connection has rights to the subscription
- the deployment package contains `backend/` and `requirements.txt`
- App Service has the right startup command if you override it

### 5. Release learning path

After dev works, practice one promotion step:

- dev App Service
- staging slot
- production slot

That is the most useful pattern to understand for KT discussions.

## How the app is structured

- `/backend` contains the Django API.
- `/api/health/live` and `/api/health/ready` support basic monitoring.
- `/api/tasks` provides CRUD for the task board.

## Questions to ask in KT

- Which secrets are stored in Key Vault and which are still pipeline variables?
- Which APIM policies are mandatory for the real project?
- Is the App Service deployed from source, zip, or container?
- Which Azure Policy assignments are required in the subscription?
- How are application logs and metrics queried during incidents?

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver 0.0.0.0:8000
```

## Build for Azure

```bash
python backend/manage.py check
python backend/manage.py collectstatic --noinput
```

If you use Azure DevOps, let the pipeline do the same checks before deployment.
