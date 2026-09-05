import csv
from datetime import datetime
from collections import defaultdict
from statistics import mean


# ==============================
# Risk thresholds
# ==============================

LARGE_TRANSACTION_THRESHOLD = 100000
NEW_PAYEE_BURST_COUNT = 3

ODD_HOUR_START = 0
ODD_HOUR_END = 5

PATTERN_DEVIATION_MULTIPLIER = 3


# ==============================
# Data loading
# ==============================

def load_transactions(file_path):
    """Load transactions from CSV and add a traceable transaction ID."""

    transactions = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            row["transaction_id"] = f"TXN-{index:03d}"
            row["amount"] = float(row["amount"])
            transactions.append(row)

    return transactions


# ==============================
# Rule 1: Large transactions
# ==============================

def detect_large_transactions(transactions):

    findings = []

    for transaction in transactions:

        if transaction["amount"] >= LARGE_TRANSACTION_THRESHOLD:

            findings.append({
                "rule": "LARGE_TRANSACTION",
                "transaction_ids": [
                    transaction["transaction_id"]
                ],
                "transactions": [
                    transaction
                ],
                "reason": (
                    f"Transaction amount ₹{transaction['amount']:,.0f} "
                    f"exceeds the large transaction threshold of "
                    f"₹{LARGE_TRANSACTION_THRESHOLD:,.0f}."
                )
            })

    return findings


# ==============================
# Rule 2: New-payee burst
# ==============================

def detect_new_payee_bursts(transactions):

    grouped = defaultdict(list)

    # Group transactions by date and payee
    for transaction in transactions:

        timestamp = datetime.fromisoformat(transaction["date"])

        key = (
            timestamp.date(),
            transaction["payee"]
        )

        grouped[key].append(transaction)

    findings = []

    for (date, payee), txns in grouped.items():

        if len(txns) < NEW_PAYEE_BURST_COUNT:
            continue

        # Check whether payee appeared before this date
        appeared_before = any(
            previous["payee"] == payee
            and datetime.fromisoformat(previous["date"]).date() < date
            for previous in transactions
        )

        # Only flag if this is a new payee
        if not appeared_before:

            total = sum(
                txn["amount"]
                for txn in txns
            )

            findings.append({
                "rule": "NEW_PAYEE_BURST",
                "payee": payee,
                "date": str(date),
                "transaction_ids": [
                    txn["transaction_id"]
                    for txn in txns
                ],
                "transactions": txns,
                "reason": (
                    f"New payee '{payee}' received "
                    f"{len(txns)} transactions on {date}, "
                    f"totaling ₹{total:,.0f}."
                )
            })

    return findings


# ==============================
# Rule 3: Odd-hour transactions
# ==============================

def detect_odd_hour_transactions(transactions):

    findings = []

    for transaction in transactions:

        timestamp = datetime.fromisoformat(
            transaction["date"]
        )

        if ODD_HOUR_START <= timestamp.hour < ODD_HOUR_END:

            findings.append({
                "rule": "ODD_HOUR",
                "transaction_ids": [
                    transaction["transaction_id"]
                ],
                "transactions": [
                    transaction
                ],
                "reason": (
                    f"Transaction occurred at "
                    f"{timestamp.strftime('%H:%M')}, "
                    f"which is within the unusual-hours "
                    f"window of 00:00–05:00."
                )
            })

    return findings


# ==============================
# Rule 4: Pattern deviation
# ==============================

def detect_pattern_deviation(transactions):

    # Only analyze bank transfers
    transfers = [
        txn for txn in transactions
        if txn["channel"] == "bank_transfer"
    ]

    if len(transfers) < 5:
        return []

    split_index = int(len(transfers) * 0.8)

    historical = transfers[:split_index]
    recent = transfers[split_index:]

    historical_amounts = [
        txn["amount"]
        for txn in historical
        if txn["amount"] > 0
    ]

    if not historical_amounts:
        return []

    normal_average = mean(historical_amounts)

    findings = []

    for transaction in recent:

        amount = transaction["amount"]

        if amount > normal_average * PATTERN_DEVIATION_MULTIPLIER:

            deviation_ratio = (
                amount / normal_average
            )

            findings.append({
                "rule": "PATTERN_DEVIATION",
                "transaction_ids": [
                    transaction["transaction_id"]
                ],
                "transactions": [
                    transaction
                ],
                "normal_average": normal_average,
                "deviation_ratio": deviation_ratio,
                "reason": (
                    f"Transaction amount ₹{amount:,.0f} "
                    f"is {deviation_ratio:.1f}x the customer's "
                    f"historical bank-transfer average of "
                    f"₹{normal_average:,.0f}."
                )
            })

    return findings


# ==============================
# Main analysis
# ==============================

def analyze_transactions(file_path):

    transactions = load_transactions(file_path)

    large_transactions = detect_large_transactions(
        transactions
    )

    new_payee_bursts = detect_new_payee_bursts(
        transactions
    )

    odd_hour_transactions = detect_odd_hour_transactions(
        transactions
    )

    pattern_deviations = detect_pattern_deviation(
        transactions
    )

    all_findings = (
        large_transactions
        + new_payee_bursts
        + odd_hour_transactions
        + pattern_deviations
    )

    # Determine investigation priority
    if any(
        finding["rule"] == "NEW_PAYEE_BURST"
        for finding in all_findings
    ):
        priority = "HIGH"

    elif all_findings:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    return {
        "attention_needed": len(all_findings) > 0,
        "investigation_priority": priority,
        "transaction_count": len(transactions),
        "findings": all_findings
    }