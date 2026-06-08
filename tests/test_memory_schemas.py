from jay.memory.schemas import MemoryCreate, MemoryKind


def test_memory_create_defaults_are_founder_safe() -> None:
    memory = MemoryCreate(kind=MemoryKind.idea, title="JAY", body="Preserve intent.")

    assert memory.source == "manual"
    assert memory.importance == 3
    assert memory.trust.confidence_score == 0.7
    assert memory.trust.assumptions == []

