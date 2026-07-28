import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o"

PROMPT = """
You are a smart legal contract auditor.

Analyze the contract and return ONLY valid JSON using this schema:

{
    "sensitive_data": [],
    "expiry_date": null,
    "redacted_text": ""
}

Sensitive data includes:

- Person names
- Company names
- CIN / Passport / ID numbers
- Financial amounts
- Addresses

Replace every sensitive element with [REDACTED].

Return expiry_date in YYYY-MM-DD format.

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