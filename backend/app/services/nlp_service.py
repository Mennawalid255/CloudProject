import re

def extract_fields(text):
    total = re.search(r"\d+\$", text)
    date = re.search(r"\d{4}-\d{2}-\d{2}", text)

    return {
        "company_name": "Unknown",
        "date": date.group() if date else None,
        "address": "Unknown",
        "total_amount": total.group() if total else None
    }