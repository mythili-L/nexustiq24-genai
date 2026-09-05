TRACK_ID=PS06

# RiskLens — Transaction Risk Investigation Assistant

> A grounded GenAI assistant for investigating unusual customer transaction activity.

RiskLens is a banking transaction-risk investigation assistant built for the NexusTiQ24 GenAI Hackathon — **PS06: Banking — Transaction Risk Investigation Assistant**.

The system analyzes a customer's transaction history using deterministic Python-based risk rules, converts the detected findings into structured evidence, and uses **Google Gemini** to generate a grounded investigation report for a human investigator.

RiskLens is designed as an **investigation-support system**, not an autonomous fraud-detection or fraud-decision system.

---

## 1. Problem Statement

Bank investigators may need to review several months of customer transaction history to identify activity that requires additional investigation.

Important signals can include:

- unusually large transfers
- multiple transactions to a newly observed payee
- transactions occurring during unusual hours
- transaction amounts that significantly differ from the customer's established transaction pattern

Manually identifying these signals across a transaction history can be time-consuming.

RiskLens addresses this problem by combining:

1. **Deterministic transaction analysis** for factual risk detection
2. **Evidence-based GenAI reasoning** for explanation and report generation
3. **Human investigation** as the final decision-making step

---

# 2. Solution Overview

RiskLens follows a strict separation between deterministic analysis and GenAI generation.

```text
Customer Transaction History
            |
            v
+-----------------------------+
| Python Deterministic Engine |
|                             |
| - Large transactions        |
| - New payee bursts          |
| - Odd-hour activity         |
| - Pattern deviation         |
+-----------------------------+
            |
            v
    Structured Evidence
            |
            v
+-----------------------------+
|        Google Gemini        |
|                             |
| Evidence-grounded report    |
| generation and explanation  |
+-----------------------------+
            |
            v
 Investigation Report
            |
            v
    Human Investigator

Python determines the evidence.
Gemini explains the evidence.
The investigator makes the decision.

---

# GitHub Repository

Repository:

https://github.com/mythili-L/nexustiq24-genai.git