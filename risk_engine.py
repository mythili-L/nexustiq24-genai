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
PATTERN_DEVIATION_MULTIPLIER = 5


# ==============================
# Data loading
# ==============================

def load_transactions(file_path):
    """Load transaction history from CSV."""

    transactions = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["amount"] = float(row["amount"])
            transactions.append(row)

    return transactions


# ==============================
# Rule 1: Large transactions
# ==============================

def detect_large_transactions(transactions):
    """Detect transactions above the fixed large-transaction threshold."""

    findings = []

    for transaction in transactions:

        if transaction["amount"] >= LARGE_TRANSACTION_THRESHOLD:

            findings.append({
                "rule": "LARGE_TRANSACTION",
                "transaction": transaction,
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
    """
    Detect multiple transactions to the same payee
    on the same calendar day.
    """

    grouped = defaultdict(list)

    for transaction in transactions:

        timestamp = datetime.fromisoformat(transaction["date"])

        calendar_date = timestamp.date()

        key = (calendar_date, transaction["payee"])

        grouped[key].append(transaction)

    findings = []

    for (date, payee), txns in grouped.items():

        if len(txns) >= NEW_PAYEE_BURST_COUNT:

            total = sum(txn["amount"] for txn in txns)

            findings.append({
                "rule": "NEW_PAYEE_BURST",
                "date": str(date),
                "payee": payee,
                "transactions": txns,
                "reason": (
                    f"{len(txns)} transactions were made to "
                    f"{payee} on {date}, totaling "
                    f"₹{total:,.0f}."
                )
            })

    return findings


# ==============================
# Rule 3: Odd-hour transactions
# ==============================

def detect_odd_hour_transactions(transactions):
    """Detect transactions made between midnight and 5 AM."""

    findings = []

    for transaction in transactions:

        try:
            timestamp = datetime.fromisoformat(transaction["date"])

            if ODD_HOUR_START <= timestamp.hour < ODD_HOUR_END:

                findings.append({
                    "rule": "ODD_HOUR",
                    "transaction": transaction,
                    "reason": (
                        f"Transaction occurred at "
                        f"{timestamp.strftime('%H:%M')}, "
                        f"which is within the unusual-hours "
                        f"window of 00:00–05:00."
                    )
                })

        except ValueError:
            continue

    return findings


# ==============================
# Rule 4: Deviation from normal
# ==============================

def detect_pattern_deviation(transactions):
    """
    Compare recent transactions against the customer's
    established transaction amount pattern.

    The first 80% of transactions are treated as the
    customer's established history. The remaining 20%
    are evaluated as recent activity.
    """

    if len(transactions) < 10:
        return []

    split_index = int(len(transactions) * 0.8)

    historical = transactions[:split_index]
    recent = transactions[split_index:]

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

            deviation_ratio = amount / normal_average

            findings.append({
                "rule": "PATTERN_DEVIATION",
                "transaction": transaction,
                "normal_average": normal_average,
                "deviation_ratio": deviation_ratio,
                "reason": (
                    f"Transaction amount ₹{amount:,.0f} is "
                    f"{deviation_ratio:.1f}x the customer's "
                    f"historical average transaction amount "
                    f"of ₹{normal_average:,.0f}."
                )
            })

    return findings


# ==============================
# Main analysis
# ==============================

def analyze_transactions(file_path):
    """Run all deterministic transaction risk checks."""

    transactions = load_transactions(file_path)

    large_transactions = detect_large_transactions(
        transactions
    )

    payee_bursts = detect_new_payee_bursts(
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
        + payee_bursts
        + odd_hour_transactions
        + pattern_deviations
    )

    return {
        "attention_needed": len(all_findings) > 0,
        "transaction_count": len(transactions),
        "findings": all_findings
    }