import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  retries: 0,
  use: { baseURL: "http://localhost:3000", browserName: "chromium" },
});
