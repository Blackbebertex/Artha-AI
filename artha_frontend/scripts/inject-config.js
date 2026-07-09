/**
 * Injects production BACKEND_URL into config.js for Render static deploy.
 */
const fs = require("fs");
const path = require("path");

const raw =
  process.env.BACKEND_URL ||
  process.env.RENDER_EXTERNAL_URL ||
  process.env.VITE_BACKEND_URL ||
  "";
const backendUrl = raw
  ? (raw.startsWith("http") ? raw : `https://${raw}`)
  : "http://localhost:8000";

if (process.env.VERCEL && !raw) {
  console.warn("WARNING: BACKEND_URL is not set — frontend will use localhost.");
}

const config = `// Auto-generated at build time
window.ARTHA_CONFIG = {
  BACKEND_URL: "${backendUrl.replace(/\/$/, "")}",
};
`;

const out = path.join(__dirname, "..", "config.js");
fs.writeFileSync(out, config, "utf8");
console.log("Wrote config.js with BACKEND_URL =", backendUrl);
