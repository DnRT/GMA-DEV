import httpx
import logging
from src.core.models import Incident
from src.plugins.base import BasePlugin
from src.config import settings

logger = logging.getLogger("AIEnricherPlugin")


class AIEnricherPlugin(BasePlugin):
    """
    AI Incident Enrichment Plugin.
    Enriches sanitized incidents with automated root-cause analysis and actionable triage recommendations.
    Supports Ollama (offline local LLM), OpenAI, and Google Gemini.
    """

    @property
    def name(self) -> str:
        return "ai_enricher"

    async def on_incident_post_sanitize(self, incident: Incident) -> Incident:
        if not settings.AI_ENRICHER_ENABLED:
            return incident

        prompt = (
            f"You are a Senior DevOps SRE. Provide a concise 2-sentence diagnostic and recommended immediate action for this incident:\n"
            f"Service: {incident.service_name}\n"
            f"Title: {incident.title}\n"
            f"Details: {incident.description}\n"
            f"HTTP Status: {incident.status_code}\n"
            f"Endpoint: {incident.endpoint}\n"
            f"Keep it purely technical, objective, and under 50 words."
        )

        analysis = None
        try:
            if settings.AI_PROVIDER == "ollama":
                analysis = await self._call_ollama(prompt)
            elif settings.AI_PROVIDER == "openai":
                analysis = await self._call_openai(prompt)
            elif settings.AI_PROVIDER == "gemini":
                analysis = await self._call_gemini(prompt)
        except Exception as e:
            logger.error(f"AI enrichment failed: {str(e)}")

        if analysis:
            incident.ai_analysis = analysis

        return incident

    async def _call_ollama(self, prompt: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                return res.json().get("response", "").strip()
        return ""

    async def _call_openai(self, prompt: str) -> str:
        if not settings.OPENAI_API_KEY:
            return ""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
        return ""

    async def _call_gemini(self, prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            return ""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return ""
