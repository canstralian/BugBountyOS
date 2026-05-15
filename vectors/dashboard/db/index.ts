import { drizzle } from "drizzle-orm/neon-serverless";
import ws from "ws";
import * as schema from "@db/schema";

function requireDatabaseUrl(): string {
  const databaseUrl = process.env.DATABASE_URL;

  if (!databaseUrl) {
    throw new Error("DATABASE_URL is required to initialize the dashboard database client");
  }

  return databaseUrl;
}

export const db = drizzle({
  connection: requireDatabaseUrl(),
  schema,
import ws from "ws";
import * as schema from "@db/schema";
import { Pool, neonConfig } from "@neondatabase/serverless";

neonConfig.webSocketConstructor = ws;

function requireDatabaseUrl(): string {
  const databaseUrl = process.env.DATABASE_URL;

  if (!databaseUrl) {
    throw new Error("DATABASE_URL is required to initialize the dashboard database client");
  }

  return databaseUrl;
}

const pool = new Pool({ connectionString: requireDatabaseUrl() });
export const db = drizzle(pool, { schema });
