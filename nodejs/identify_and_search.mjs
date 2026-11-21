import fs from "node:fs";
import path from "node:path";

const API_KEY = process.env.KARANFIL_API_KEY;
const BASE_URL = "https://api.karanfillabs.com";

if (!API_KEY) throw new Error("Set KARANFIL_API_KEY environment variable first.");

async function identifyFrame(imagePath, topK = 5, minScore = 0.7) {
  const form = new FormData();
  const bytes = fs.readFileSync(imagePath);
  form.append("file", new Blob([bytes], { type: "image/jpeg" }), path.basename(imagePath));

  const url = `${BASE_URL}/v1/identify?top_k=${topK}&min_score=${minScore}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
    body: form,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

async function semanticSearch(query, topK = 5) {
  const res = await fetch(`${BASE_URL}/v1/search`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

const arg = process.argv[2];
const result = arg && fs.existsSync(arg)
  ? await identifyFrame(arg)
  : await semanticSearch(arg || "rainy neon street at night");

console.log(JSON.stringify(result, null, 2));
