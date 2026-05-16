export const openapiDocument = {
  openapi: "3.0.3",
  info: {
    title: "Azure Learning Lab API",
    version: "1.0.0",
    description: "A small API for learning Azure App Service, APIM, Key Vault references, and DevOps deployment flows."
  },
  servers: [{ url: "/" }],
  paths: {
    "/health/live": {
      get: {
        summary: "Liveness probe",
        responses: {
          "200": { description: "Service is alive" }
        }
      }
    },
    "/health/ready": {
      get: {
        summary: "Readiness probe",
        responses: {
          "200": { description: "Service is ready" }
        }
      }
    },
    "/api/config": {
      get: {
        summary: "Public app configuration",
        responses: {
          "200": { description: "Configuration payload" }
        }
      }
    },
    "/api/tasks": {
      get: {
        summary: "List tasks",
        responses: {
          "200": { description: "Task list" }
        }
      },
      post: {
        summary: "Create task",
        responses: {
          "201": { description: "Task created" }
        }
      }
    },
    "/api/tasks/{id}": {
      put: {
        summary: "Update task",
        responses: {
          "200": { description: "Task updated" },
          "404": { description: "Task not found" }
        }
      },
      delete: {
        summary: "Delete task",
        responses: {
          "204": { description: "Task deleted" },
          "404": { description: "Task not found" }
        }
      }
    }
  }
};
