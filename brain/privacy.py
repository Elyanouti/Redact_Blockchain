from brain.auditor import audit_contract


def remove_sensitive_information(text):
    analysis = audit_contract(text)
    redacted_text = analysis.get("redacted_text", text)

    if "\\n" in redacted_text and "\n" not in redacted_text:
        redacted_text = redacted_text.replace("\\n", "\n")
    if "\\r\\n" in redacted_text and "\r\n" not in redacted_text:
        redacted_text = redacted_text.replace("\\r\\n", "\r\n")

    return {
        "redacted_text": redacted_text,
        "redacted_items": analysis.get("redacted_items", []),
    }
