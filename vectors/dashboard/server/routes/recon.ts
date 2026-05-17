import { Router } from "express";
import { z } from "zod";

const router = Router();

const PIPELINE_URL = process.env.PIPELINE_URL ?? "http://localhost:5001";

const scanRequestSchema = z.object({
  target: z.string().min(1),
  scanType: z.enum(["quick", "full", "stealth"]),
});

// Scan types map to finding kinds sent as pipeline events
const SCAN_KIND: Record<string, string> = {
  quick: "recon:quick",
  full: "recon:full",
  stealth: "recon:stealth",
};

router.post("/scan", async (req, res) => {
  const parsed = scanRequestSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(422).json({ error: parsed.error.flatten() });
    return;
  }

  const { target, scanType } = parsed.data;

  const response = await fetch(`${PIPELINE_URL}/api/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target,
      findings: [{ kind: SCAN_KIND[scanType], value: target, confidence: 1.0 }],
      timestamp: new Date().toISOString(),
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    res.status(502).json({ error: "pipeline rejected event", detail: body });
    return;
  }

  const actionPlan = await response.json();
  res.status(202).json(actionPlan);
});

export const reconRouter = router;
