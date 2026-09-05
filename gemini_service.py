import os
from dotenv import load_dotenv
from google import genai

from risk_engine import analyze_transactions


# ==============================
# Configuration
# ==============================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


# ==============================
# Load system prompt
# ==============================

def load_system_prompt():

    with open(
        "prompts/system_prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==============================
# Generate investigation report
# ==============================

def generate_investigation_report(evidence):

    system_prompt = load_system_prompt()

    prompt = f"""
{system_prompt}

Here is the deterministic evidence produced by the RiskLens
transaction risk engine.

IMPORTANT:
Treat this evidence as the source of truth.

EVIDENCE:

{evidence}

Generate the investigation report now.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# ==============================
# Main test
# ==============================

if __name__ == "__main__":

    evidence = analyze_transactions(
        "data/transactions.csv"
    )

    report = generate_investigation_report(
        evidence
    )

    print()
    print("=" * 60)
    print("RISK LENS INVESTIGATION REPORT")
    print("=" * 60)
    print()
    print(report)