from runbook_generator.redaction import redact_text


def test_redacts_bearer_and_api_key() -> None:
    text = "Bearer abcdefghijklmnopqrstuvwxyz123456 and api_key=prod_secret_value"

    redacted, count = redact_text(text)

    assert count == 2
    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "prod_secret_value" not in redacted
    assert "[REDACTED]" in redacted
