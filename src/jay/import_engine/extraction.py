import json
import logging
from typing import List, Dict, Any
from jay.memory.models import MemoryItem

from jay.config import get_settings

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Uses the local LLM to extract structured JAY memory events from raw text."""

    def __init__(self):
        self.settings = get_settings()

    async def extract_memories(self, text: str, source: str) -> List[Dict[str, Any]]:
        """
        Takes raw text, chunks it if too large, and extracts memory entities.
        Returns a list of dictionaries representing the extracted memories.
        """
        # For MVP, we'll assume text fits in context. In production, use recursive chunking.
        if len(text) > 15000:
            text = text[:15000] + "...[TRUNCATED FOR LENGTH]"

        system_prompt = (
            "You are the ingestion engine for JAY, a Founder Operating System.\n"
            "Your task is to analyze the provided text and extract core entities into a STRICT JSON array.\n"
            "The possible entity kinds are: 'project', 'person', 'decision', 'task', 'commitment', 'idea', 'document', 'project_progress', 'execution_event', 'decision_signal'.\n"
            "Particularly look for:\n"
            "- 'project_progress': Updates to milestones, momentum, or overall project velocity.\n"
            "- 'execution_event': Notable shipped features, PRs, or significant commits.\n"
            "- 'decision_signal': Architectural choices or debates made in issue threads.\n"
            "For each extracted entity, you must provide:\n"
            " - 'kind': one of the allowed kinds\n"
            " - 'title': short descriptive title\n"
            " - 'body': detailed description and context\n"
            " - 'importance': integer from 1 (low) to 5 (critical). Give high importance to shifts in project momentum.\n"
            " - 'confidence': float from 0.0 to 1.0 representing how confident you are this is a real, meaningful entity\n"
            " - 'tags': list of string tags\n"
            "Output NOTHING but the JSON array. Do not include markdown blocks like ```json."
        )

        try:
            import asyncio
            from jay.engines.llm import generate_chat
            
            def _run_llm():
                return generate_chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": f"Text Source: {source}\n\nContent:\n{text}",
                        },
                    ],
                    temperature=0.1
                )

            response = await asyncio.to_thread(_run_llm)
            content = response["choices"][0]["message"]["content"].strip()

            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            data = json.loads(content.strip())
            if not isinstance(data, list):
                logger.error("LLM returned non-list JSON.")
                return []

            validated = []
            allowed_kinds = {
                "project",
                "person",
                "decision",
                "task",
                "commitment",
                "idea",
                "document",
                "project_progress",
                "execution_event",
                "decision_signal",
            }

            for item in data:
                if not isinstance(item, dict):
                    continue
                if item.get("kind") not in allowed_kinds:
                    item["kind"] = "idea"  # fallback

                validated.append(
                    {
                        "kind": item.get("kind", "idea"),
                        "title": item.get("title", "Untitled Extract"),
                        "body": item.get("body", ""),
                        "importance": int(item.get("importance", 3)),
                        "confidence": float(item.get("confidence", 0.5)),
                        "tags": item.get("tags", []),
                        "source": source,
                        "extraction_method": "llm-llama3-json",
                    }
                )

            return validated

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse LLM JSON output for {source}: {e}\nContent: {content}"
            )
            return []
        except Exception as e:
            logger.error(f"Extraction failed for {source}: {e}")
            return []
