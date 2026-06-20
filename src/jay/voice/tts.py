import asyncio
import logging
import os
import tempfile
from typing import Protocol

import edge_tts

logger = logging.getLogger(__name__)


class TTSEngine(Protocol):
    async def speak(self, text: str) -> None: ...


class EdgeTTSEngine:
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        self.voice = voice

    async def speak(self, text: str) -> None:
        if not text.strip():
            return

        logger.info(f"Speaking: {text}")

        # Generate temporary file
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(path)

            # Play using macOS native afplay
            process = await asyncio.create_subprocess_exec(
                "afplay",
                path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()
        except Exception as e:
            logger.error(f"TTS failed: {e}")
        finally:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


# Provide a default singleton for ease of use
default_engine = EdgeTTSEngine()


async def speak(text: str) -> None:
    """Helper function to use the default engine."""
    await default_engine.speak(text)
