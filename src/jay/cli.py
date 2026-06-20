import argparse
import logging
import sys

from jay.db import SessionLocal
from jay.events.engine import ReplayEngine
from jay.events.projector import DashboardProjector, GraphProjector, VectorProjector
from jay.memory.projector import MemoryProjector
from jay.trust.projector import TrustProjector
from jay.intent.projector import IntentProjector
from jay.leverage.projector import LeverageProjector
from jay.decisions.projector import DecisionProjector
from jay.founder.projector import FounderProjector

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="JAY Replay CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # rebuild-memory
    subparsers.add_parser("rebuild-memory", help="Rebuild the memory items projection")
    # rebuild-graph
    subparsers.add_parser("rebuild-graph", help="Rebuild the graph projection")
    # rebuild-vectors
    subparsers.add_parser("rebuild-vectors", help="Rebuild the vector projection")
    # rebuild-trust
    subparsers.add_parser("rebuild-trust", help="Rebuild the trust ledger projection")
    # rebuild-intent
    subparsers.add_parser("rebuild-intent", help="Rebuild the intent projection")
    # rebuild-leverage
    subparsers.add_parser("rebuild-leverage", help="Rebuild the leverage projection")
    # rebuild-decisions
    subparsers.add_parser("rebuild-decisions", help="Rebuild the decision ledger")
    # rebuild-founder
    subparsers.add_parser("rebuild-founder", help="Rebuild the founder model tables")
    # rebuild-all
    subparsers.add_parser("rebuild-all", help="Rebuild all projections")

    # speak
    speak_parser = subparsers.add_parser("speak", help="Speak text using Jarvis voice")
    speak_parser.add_argument("text", help="Text to speak")

    # daemon
    daemon_parser = subparsers.add_parser(
        "daemon", help="Run the proactive background observer daemon"
    )
    daemon_parser.add_argument(
        "--interval", type=int, default=3600, help="Interval in seconds between checks"
    )

    # listen
    listen_parser = subparsers.add_parser(
        "listen", help="Listen to the microphone and respond"
    )
    listen_parser.add_argument(
        "--continuous",
        action="store_true",
        help="Listen continuously for the wake word",
    )

    args = parser.parse_args()

    if args.command == "speak":
        import asyncio
        from jay.voice.tts import speak

        asyncio.run(speak(args.text))
        sys.exit(0)

    if args.command == "daemon":
        import asyncio
        from jay.engines.observer import ObserverDaemon

        daemon = ObserverDaemon(interval_seconds=args.interval)
        try:
            asyncio.run(daemon.run())
        except KeyboardInterrupt:
            print("\nObserver daemon shut down.")
        sys.exit(0)

    if args.command == "listen":
        import asyncio
        from jay.voice.stt import Listener
        from jay.intelligence.llm import generate_jarvis_response
        from jay.voice.tts import speak

        listener = Listener(model_size="base")

        if args.continuous:
            for text in listener.listen_continuously():
                text_lower = text.lower()
                if "jay" in text_lower:
                    print(f"\n[Wake Word Detected]: {text}")

                    context = "The Founder just spoke to you via continuous voice."
                    instruction = f"Respond to this concisely: {text}"

                    async def process_and_speak():
                        jarvis_message = await generate_jarvis_response(
                            context, instruction
                        )
                        if jarvis_message:
                            print(f"JAY: {jarvis_message}")
                            await speak(jarvis_message)
                        else:
                            await speak("I'm sorry, I could not process that.")

                    asyncio.run(process_and_speak())
                else:
                    # Ignore background chatter
                    print(f"Ignored background chatter: {text}")
            sys.exit(0)

        else:
            text = listener.listen_and_transcribe(timeout=None)

            if text:
                print(f"You said: {text}")
                context = "The Founder just spoke to you via voice."
                instruction = f"Respond to this concisely: {text}"

                async def process_and_speak():
                    jarvis_message = await generate_jarvis_response(
                        context, instruction
                    )
                    if jarvis_message:
                        print(f"JAY: {jarvis_message}")
                        await speak(jarvis_message)

                    else:
                        await speak("I'm sorry, I could not process that.")

                asyncio.run(process_and_speak())
            else:
                print("No speech detected.")

            sys.exit(0)

    projectors = []
    if args.command == "rebuild-memory":
        projectors.append(MemoryProjector())
    elif args.command == "rebuild-graph":
        projectors.append(GraphProjector())
    elif args.command == "rebuild-vectors":
        projectors.append(VectorProjector())
    elif args.command == "rebuild-trust":
        projectors.append(TrustProjector())
    elif args.command == "rebuild-intent":
        projectors.append(IntentProjector())
    elif args.command == "rebuild-leverage":
        projectors.append(LeverageProjector())
    elif args.command == "rebuild-decisions":
        projectors.append(DecisionProjector())
    elif args.command == "rebuild-founder":
        projectors.append(FounderProjector())
    elif args.command == "rebuild-all":
        projectors.extend(
            [
                MemoryProjector(),
                TrustProjector(),
                IntentProjector(),
                LeverageProjector(),
                GraphProjector(),
                VectorProjector(),
                DashboardProjector(),
                DecisionProjector(),
                FounderProjector(),
            ]
        )
    else:
        logger.error("Unknown command")
        sys.exit(1)

    with SessionLocal() as session:
        engine = ReplayEngine(session, projectors)
        try:
            engine.rebuild()
        except Exception as e:
            logger.error(f"Replay failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
