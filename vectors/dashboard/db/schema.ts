import { pgTable, text, integer, timestamp, jsonb } from "drizzle-orm/pg-core";
export const users = pgTable("users", {
  id: integer().primaryKey().generatedAlwaysAsIdentity(),
  username: text("username").unique().notNull(),
  password: text("password").notNull(),
});