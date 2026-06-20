import asyncio
import logging

logger = logging.getLogger(__name__)

class RealityPoller:
    """Base class for polling external systems when webhooks are insufficient."""
    @property
    def name(self) -> str:
        return "BasePoller"
        
    async def poll(self):
        raise NotImplementedError

class RealitySyncManager:
    """Manages active synchronization of external state into JAY."""
    def __init__(self, pollers=None):
        self.pollers = pollers or []
        
    async def run_forever(self, interval_seconds: int = 300):
        logger.info(f"RealitySyncManager online. Polling {len(self.pollers)} systems every {interval_seconds}s.")
        while True:
            for poller in self.pollers:
                try:
                    await poller.poll()
                except Exception as e:
                    logger.error(f"Poller {poller.name} failed Reality Sync: {e}")
            await asyncio.sleep(interval_seconds)
