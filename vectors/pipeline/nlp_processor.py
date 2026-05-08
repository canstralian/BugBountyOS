<<<<<<< HEAD
=======
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a bug bounty reconnaissance analyst. Given raw reconnaissance findings, "
    "produce a structured action plan with prioritized recommendations. "
    "Respond with valid JSON only — no prose outside the JSON object."
)

ACTION_PLAN_SCHEMA = """{
  "recommendations": [
    {"action": "<string>", "priority": "high|medium|low", "rationale": "<string>"}
  ],
  "confidence": <float 0-1>
}"""


def _call_claude(findings_text: str, api_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": findings_text}],
    )
    import json
    return json.loads(response.content[0].text)


def _call_mistral(findings_text: str, api_key: str) -> dict:
    import requests
    import json
    resp = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": findings_text},
            ],
            "response_format": {"type": "json_object"},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return json.loads(resp.json()["choices"][0]["message"]["content"])


>>>>>>> 185d04f (feat: implement pipeline/storage vector stubs, contracts, and dev agent team)
class NLPProcessor:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or os.environ.get("NLP_PROVIDER", "claude")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.mistral_key = os.environ.get("MISTRAL_API_KEY", "")

    def process(self, target: str, findings: list) -> dict:
        findings_text = (
            f"Target: {target}\n\nFindings:\n"
            + "\n".join(f"- [{f.get('kind','')}] {f.get('value','')} (confidence: {f.get('confidence',0)})"
                        for f in findings)
            + f"\n\nRespond using this schema:\n{ACTION_PLAN_SCHEMA}"
        )

        try:
            if self.provider == "mistral" and self.mistral_key:
                result = _call_mistral(findings_text, self.mistral_key)
                used_provider = "mistral"
            elif self.anthropic_key:
                result = _call_claude(findings_text, self.anthropic_key)
                used_provider = "claude"
            elif self.mistral_key:
                result = _call_mistral(findings_text, self.mistral_key)
                used_provider = "mistral"
            else:
                logger.warning("No AI provider configured — returning stub action plan")
                result = {"recommendations": [], "confidence": 0.0}
                used_provider = "none"
        except Exception as exc:
            logger.error("NLP provider %s failed: %s", self.provider, exc)
            result = {"recommendations": [], "confidence": 0.0}
            used_provider = "error"

        return {
            "id": str(uuid.uuid4()),
            "target": target,
            "recommendations": result.get("recommendations", []),
            "confidence": result.get("confidence", 0.0),
            "provider": used_provider,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
