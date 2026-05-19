from src.classifier import classify_email
print("Import OK")

result = classify_email(
    subject="Invoice #1234 overdue",
    body="Hi, just a reminder that invoice #1234 for $500 is now 30 days overdue. Please process payment at your earliest convenience."
)

print(result)