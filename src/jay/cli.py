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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

    args = parser.parse_args()

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
