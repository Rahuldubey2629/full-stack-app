from app.services.llm_service import generate_retrospective


def test_llm_service_mock(monkeypatch):
    def fake_call(prompt: str, incident_id: int):
        # Check which prompt we are responding to based on its content
        if "postmortem" in prompt or "incident postmortem assistant" in prompt.lower():
            return {
                "payload": {
                    "timeline": ["t1"],
                    "root_cause": "rc",
                    "impact": "impact",
                    "action_items": ["a1"],
                    "severity_score": 2,
                    "mttr_minutes": 10,
                },
                "tokens_used": 5,
            }
        else:
            return {
                "payload": {
                    "runbook_md": "# Runbook",
                },
                "tokens_used": 5,
            }

    monkeypatch.setattr("app.services.llm_service._retry_call", fake_call)
    result = generate_retrospective("input", 1)
    assert result.severity_score == 2
    assert result.runbook_md == "# Runbook"
