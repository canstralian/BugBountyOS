import { Router } from "express";
import fetch from "node-fetch";

const router = Router();

// Airtable configuration for the BugBountyOS Kernel
const AIRTABLE_BASE_ID = "appT4zR1ybxgrujBD";
const AIRTABLE_TABLE_NAME = "Programs";

router.get("/", async (req, res) => {
  try {
    const apiKey = process.env.AIRTABLE_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: "Airtable API key not configured in environment" });
    }

    const response = await fetch(
      `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${AIRTABLE_TABLE_NAME}`,
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Airtable API error: ${error}`);
    }

    const data = await response.json();
    // Return the raw records; the usePrograms hook handles the mapping
    res.json(data.records);
  } catch (error: any) {
    console.error("Error fetching programs from Airtable:", error);
    res.status(500).json({ error: "Failed to fetch programs from security kernel" });
  }
});

export const programsRouter = router;
