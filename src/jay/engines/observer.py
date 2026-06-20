import asyncio
import logging
from typing import Set

from jay.db import SessionLocal
from jay.engines.opportunity import OpportunityEngine
from jay.voice.tts import speak
from jay.intelligence.llm import generate_jarvis_response

logger = logging.getLogger(__name__)


class ObserverDaemon:
    def __init__(self, interval_seconds: int = 3600):
        # Default to 1 hour, or whatever is specified
        self.interval_seconds = interval_seconds
        self.announced_opportunities: Set[str] = set()

    async def run(self) -> None:
        logger.info(
            f"Observer Daemon started. Checking every {self.interval_seconds} seconds."
        )
        await speak("Observer Daemon online. I am monitoring your business systems.")

        while True:
            try:
                await self._check_opportunities()
            except Exception as e:
                logger.error(f"Error during observer check: {e}")

            await asyncio.sleep(self.interval_seconds)

    async def _check_opportunities(self) -> None:
        logger.info("Scanning for high-leverage opportunities...")
        with SessionLocal() as session:
            engine = OpportunityEngine(session)
            opportunities = engine.analyze()

            for opp in opportunities:
                opp_id = str(opp.entity_id)
                if opp_id not in self.announced_opportunities:
                    logger.info(
                        f"Announcing opportunity: {opp.opportunity_type} - {opp.entity_title}"
                    )

                    context = f"Opportunity Type: {opp.opportunity_type}\nItem Title: {opp.entity_title}\nReason: {opp.evidence}"
                    instruction = f"Inform the Founder about this opportunity and recommend: {opp.recommended_action}"

                    jarvis_message = await generate_jarvis_response(
                        context, instruction
                    )

                    # Fallback if LLM fails or is not running
                    if not jarvis_message:
                        jarvis_message = f"Sir, I have detected a high leverage opportunity regarding {opp.entity_title}. {opp.recommended_action}"

                    await speak(jarvis_message)

                    # Mark as announced
                    self.announced_opportunities.add(opp_id)

                    # We announce only the top opportunity per cycle to avoid overwhelming the Founder
                    break
