from jay.chief_of_staff.leverage_ranker import LeverageRanker, CandidateAction

def test_leverage_priority_score():
    ranker = LeverageRanker()
    action = CandidateAction(
        statement="Test",
        reason="Test",
        impact=10.0,
        urgency=10.0,
        intent_alignment=10.0,
        trust=10.0,
        reversibility=10.0
    )
    score = ranker.score(action)
    assert score == 10.0  # (3.5 + 2.5 + 2.0 + 1.0 + 1.0)
    
    action2 = CandidateAction(
        statement="Test2",
        reason="Test",
        impact=5.0, # 1.75
        urgency=5.0, # 1.25
        intent_alignment=10.0, # 2.0
        trust=0.0,
        reversibility=0.0
    )
    assert ranker.score(action2) == 5.0
    
def test_leverage_ranking():
    ranker = LeverageRanker()
    a1 = CandidateAction("Low", "", 2.0, 2.0, 2.0, 2.0, 2.0)
    a2 = CandidateAction("High", "", 9.0, 9.0, 9.0, 9.0, 9.0)
    
    ranked = ranker.rank([a1, a2])
    assert ranked[0][0].statement == "High"
    assert ranked[1][0].statement == "Low"
