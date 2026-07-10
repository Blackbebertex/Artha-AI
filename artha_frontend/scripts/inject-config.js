/**
 * Bakes BACKEND_URL into config.js at build time (Vercel, Render, local).
 */
const fs = require("fs");
const path = require("path");

const DEFAULT_PROD_API = "https://artha-api-lsli.onrender.com";

const raw =
  process.env.BACKEND_URL ||
  process.env.RENDER_EXTERNAL_URL ||
  process.env.VITE_BACKEND_URL ||
  "";

const isVercel = Boolean(process.env.VERCEL);

if (isVercel && !raw) {
  console.warn(
    "\n[artha-frontend] WARNING: BACKEND_URL not set in Vercel env.\n" +
      `  Using default: ${DEFAULT_PROD_API}\n` +
      "  Set BACKEND_URL in Vercel → Settings → Environment Variables to override.\n"
  );
}

const backendUrl = raw
  ? (raw.startsWith("http") ? raw : `https://${raw}`)
  : isVercel
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL || process.env.VERCEL_URL || "arthaai-two.vercel.app"}`
    : "http://localhost:8000";

const config = `// Auto-generated at build - do not edit
window.ARTHA_CONFIG = {
  BACKEND_URL: "${backendUrl.replace(/\/$/, "")}",
};
(function () {
  var params = new URLSearchParams(window.location.search);
  var override = params.get("api") || params.get("backend");
  if (override) {
    window.ARTHA_CONFIG.BACKEND_URL = override.startsWith("http")
      ? override.replace(/\\/$/, "")
      : "https://" + override.replace(/\\/$/, "");
  }
})();
`;

const out = path.join(__dirname, "..", "config.js");
fs.writeFileSync(out, config, "utf8");
console.log("[artha-frontend] config.js → BACKEND_URL =", backendUrl);
