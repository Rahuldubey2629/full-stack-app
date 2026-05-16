import { z } from "zod";

const envSchema = z.object({
  APP_NAME: z.string().default("Azure Learning Lab"),
  APP_MESSAGE: z.string().default("Practical Azure demo for App Service, APIM, Key Vault, and DevOps."),
  CORS_ORIGIN: z.string().optional(),
  NODE_ENV: z.string().default("development"),
  PORT: z.coerce.number().default(3000)
});

export const config = envSchema.parse(process.env);

export function getAllowedOrigins(): string[] {
  return config.CORS_ORIGIN?.split(",").map((origin) => origin.trim()).filter(Boolean) ?? [];
}
