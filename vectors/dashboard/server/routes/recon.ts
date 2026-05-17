import { Router } from "express";
import { z } from "zod";

interface ScanResult {
  domain: string;
  scanType: ScanType;
  scanFlags: string[];
  timestamp: string;
  whois: null;
  dns: {
    a: string[];
    mx: string[];
    ns: string[];
    txt: string[];
  };
  ports: Array<{
    port: number;
    service: string;
    protocol: string;
  }>;
  technologies: string[];
}

const router = Router();

const scanConfigs = {
  quick: ["-F"],
  full: ["-p-"],
  stealth: ["-sS", "-T2"],
} as const;

const scanTypes = Object.keys(scanConfigs) as [
  keyof typeof scanConfigs,
  ...(keyof typeof scanConfigs)[],
];
type ScanType = keyof typeof scanConfigs;

const targetSchema = z.string().trim().min(1, "target is required");

const scanRequestSchema = z.object({
  target: targetSchema,
  scanType: z.enum(scanTypes),
});

function extractHostname(target: string): string {
  const normalizedTarget = /^[a-z][a-z0-9+.-]*:\/\//i.test(target)
    ? target
    : `https://${target}`;

  const hostname = new URL(normalizedTarget).hostname;

  if (!hostname) {
    throw new Error("target must include a hostname");
  }

  return hostname;
}

async function performRecon(domain: string, scanType: ScanType): Promise<ScanResult> {
  return {
    domain,
    scanType,
    scanFlags: [...scanConfigs[scanType]],
    timestamp: new Date().toISOString(),
    whois: null,
    dns: { a: [], mx: [], ns: [], txt: [] },
    ports: [],
    technologies: [],
  };
}

router.post("/scan", async (req, res) => {
  const parsedRequest = scanRequestSchema.safeParse(req.body);

  if (!parsedRequest.success) {
    return res.status(400).json({
      error: "Invalid recon scan request",
      details: parsedRequest.error.flatten().fieldErrors,
    });
  }

  try {
    const { target, scanType } = parsedRequest.data;
    const domain = extractHostname(target);
    return res.json(await performRecon(domain, scanType));
  } catch (error) {
    if (error instanceof TypeError) {
      return res.status(400).json({ error: "target must be a valid URL or hostname" });
    }

    if (error instanceof Error && error.message === "target must include a hostname") {
      return res.status(400).json({ error: error.message });
    }

    console.error("Recon scan failed", { error });
    return res.status(500).json({ error: "Recon scan failed" });
  }
});

export const reconRouter = router;
