def analyze_receipt(receipt_text):
    items = receipt_text.split(",")
    return [item.strip() for item in items]