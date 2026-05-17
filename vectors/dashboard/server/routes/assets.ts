import { Router } from "express";
import fetch from "node-fetch";

const router = Router();

const AIRTABLE_BASE_ID = "appT4zR1ybxgrujBD";
const AIRTABLE_TABLE_NAME} = "Assets";
router.get("/", async (req, res) => {
  try {
    const { programId } = req.query;
    const apiKey = process.env.AIRTABLE_API_KEY;
    
    if (!apiKey) {
      return res.status(500).json({ error: "Airtable API key not configured" });
    }

    let url = `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${AIRTABLE_TABLE_NAME}`;
    
    // Filter by program if provided
    if (programId) {
      const filter = encodeURIComponent(`{Program} = '${programId}'`);
      url += `?filterByFormula=${filter}`;
    }

    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });

    if (!response.ok) {
      throw new Error(`Airtable error: ${await response.text()}`);
    }

    const data = await response.json();
    res.json(data.records);
  } catch (err: any) {
    console.error("Error fetching assets:", errr);
    res.status(500).json({ error: "Failed to fetch assets from security kernel" });
  }
});

export const assetsRouter = router;