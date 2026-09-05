from risk_engine import analyze_transactions


result = analyze_transactions("data/transactions.csv")

print("Attention needed:", result["attention_needed"])
print("Investigation priority:", result["investigation_priority"])
print("Transaction count:", result["transaction_count"])
print()

for finding in result["findings"]:

    print("RULE:", finding["rule"])
    print("TRANSACTION IDs:", finding["transaction_ids"])
    print("REASON:", finding["reason"])
    print()