import cors from "cors";
import express from "express";
import fs from "node:fs";
import path from "node:path";
import helmet from "helmet";
import morgan from "morgan";

import { config, getAllowedOrigins } from "./config.js";
import { openapiDocument } from "./openapi.js";
import { createTask, deleteTask, getTaskSummary, listTasks, taskCreateSchema, taskUpdateSchema, updateTask } from "./tasks.js";

const clientBuildPath = path.resolve(process.cwd(), "dist/client");
const clientIndexPath = path.join(clientBuildPath, "index.html");

export function createApp() {
  const app = express();
  const allowedOrigins = getAllowedOrigins();

  app.disable("x-powered-by");
  app.use(helmet({ contentSecurityPolicy: false }));
  app.use(
    cors({
      origin: allowedOrigins.length > 0 ? allowedOrigins : true
    })
  );
  app.use(express.json());
  app.use(morgan(config.NODE_ENV === "production" ? "combined" : "dev"));

  app.get("/health/live", (_request, response) => {
    response.json({ status: "alive", uptimeSeconds: Math.round(process.uptime()) });
  });

  app.get("/health/ready", (_request, response) => {
    response.json({ status: "ready", environment: config.NODE_ENV });
  });

  app.get("/openapi.json", (_request, response) => {
    response.json(openapiDocument);
  });

  app.get("/api/config", (_request, response) => {
    response.json({
      appName: config.APP_NAME,
      message: config.APP_MESSAGE,
      environment: config.NODE_ENV,
      hasSecretConfigured: Boolean(process.env.APP_SECRET),
      apiVersion: "v1"
    });
  });

  app.get("/api/tasks", (_request, response) => {
    response.json({ tasks: listTasks(), summary: getTaskSummary() });
  });

  app.post("/api/tasks", (request, response) => {
    const parsed = taskCreateSchema.safeParse(request.body);

    if (!parsed.success) {
      response.status(400).json({ message: "Invalid task payload", issues: parsed.error.flatten() });
      return;
    }

    const task = createTask(parsed.data);
    response.status(201).json({ task });
  });

  app.put("/api/tasks/:id", (request, response) => {
    const parsed = taskUpdateSchema.safeParse(request.body);

    if (!parsed.success) {
      response.status(400).json({ message: "Invalid task payload", issues: parsed.error.flatten() });
      return;
    }

    const updatedTask = updateTask(request.params.id, parsed.data);

    if (!updatedTask) {
      response.status(404).json({ message: "Task not found" });
      return;
    }

    response.json({ task: updatedTask });
  });

  app.delete("/api/tasks/:id", (request, response) => {
    const removed = deleteTask(request.params.id);

    if (!removed) {
      response.status(404).json({ message: "Task not found" });
      return;
    }

    response.status(204).send();
  });

  if (fs.existsSync(clientIndexPath)) {
    app.use(express.static(clientBuildPath));

    app.get(/^(?!\/api|\/health|\/openapi\.json).*/, (_request, response) => {
      response.sendFile(clientIndexPath);
    });
  }

  app.use((_request, response) => {
    response.status(404).json({ message: "Route not found" });
  });

  return app;
}
