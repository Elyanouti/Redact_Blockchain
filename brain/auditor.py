import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o"

PROMPT = """
You are an AI specialized in privacy protection for legal contracts.

Your task is to identify and redact all sensitive or personally identifiable information (PII) while preserving the original structure and formatting of the contract.

Sensitive information includes, but is not limited to:

- Full names
- Company names
- Email addresses
- Phone numbers
- Physical addresses
- National ID, Passport or CIN numbers
- Tax identification numbers
- Bank account numbers
- IBAN
- Credit card numbers
- Financial amounts
- Signatures
- Dates of birth
- Any information that could identify a person or organization

Replace every detected sensitive value with:

[REDACTED]

Do NOT summarize the contract.
Do NOT rewrite the contract.
Do NOT change legal clauses.
Do NOT modify formatting except replacing sensitive values.
Preserve original line breaks and paragraph layout exactly.
Do not collapse the text into a single line.

Return ONLY valid JSON using this schema:

{
    "redacted_text": "...",
    "redacted_items": [
        {
            "type": "",
            "original": ""
        }
    ]
}

Return ONLY JSON.
"""

def audit_contract(text):

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)

    except Exception:

        match = re.search(r"\{[\s\S]*\}", content)

        if match:
            return json.loads(match.group())

        raise Exception("Invalid JSON returned from OpenAI.")