import re


def clean_text(text: str):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def extract_first_valid_line(lines):
    blacklist = [
        "invoice", "total", "date", "vat", "tax", "amount",
        "receipt", "time", "auth", "batch", "sale",
        "master", "approved", "customer", "copy",
        "merchant", "contactless", "banque"
    ]

    best_line = None
    best_score = -1

    for line in lines[:12]:
        line = line.strip()

        if len(line) < 4:
            continue

        score = 0

        if any(word in line.lower() for word in blacklist):
            continue

        if not any(c.isalpha() for c in line):
            continue

 
        letters = [c for c in line if c.isalpha()]
        upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)

        score += upper_ratio * 10

        if "-" in line:
            score += 3

        if re.search(r"\d", line):
            score -= 5

        if len(line.split()) <= 4:
            score += 2

        if score > best_score:
            best_score = score
            best_line = line

        if best_line:
            best_line = re.sub(r"^[=~\-\s]+", "", best_line)

    return best_line


def find_by_keywords(text, keywords):
    for line in text.split("\n"):
        if any(k.lower() in line.lower() for k in keywords):
            match = re.search(r"(\d+(?:[\.,]\d+)?)", line)
            if match:
                return match.group(1)
    return None


def extract_possible_totals(text):
    return [float(x) for x in re.findall(r"\d+\.\d{2}", text)]


def parse_invoice(text: str):

    data = {}

    text = clean_text(text)
    lines = text.split("\n")


    data["company_name"] = extract_first_valid_line(lines)


    date_match = re.search(
        r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}",
        text
    )
    data["date"] = date_match.group() if date_match else None


    total = find_by_keywords(
        text,
        ["total", "grand total", "amount", "amount due", "balance"]
    )

    if not total:
        possible = extract_possible_totals(text)
        if possible:
            total = max(possible)

    data["total price"] = total


    data["vat"] = find_by_keywords(text, ["vat"])
    data["tax"] = find_by_keywords(text, ["tax"])


    invoice_match = re.search(
        r"(invoice\s*(no|number|#|id)?)[^\w\d]*([A-Z0-9\-\/]+)",
        text,
        re.I
    )

    if not invoice_match:
        invoice_match = re.search(r"\bINV[- ]?\d+\b", text, re.I)

    data["invoice_number"] = (
        invoice_match.group(3)
        if invoice_match and len(invoice_match.groups()) >= 3
        else invoice_match.group(0)
        if invoice_match
        else None
    )


    errors = []

    if data["total price"]:
        try:
            data["total price"] = float(data["total price"])
        except:
            errors.append("Invalid total format")

    if data["date"] and not re.match(r"\d{2}[/-]\d{2}[/-]\d{4}", data["date"]):
        errors.append("Invalid date format")

    if data["invoice_number"] and len(data["invoice_number"]) < 3:
        errors.append("Invalid invoice number")

    if data["company_name"] and len(data["company_name"]) < 3:
        errors.append("Invalid company name")

    return {
        "data": data,
        "errors": errors,
        "is_valid": len(errors) == 0
    }