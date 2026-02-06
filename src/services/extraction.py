import re
from datetime import datetime

class ExtractionService:
    def __init__(self):
        # Compiled regex patterns for performance
        self.gst_pattern = re.compile(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}')
        # Common date formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')
        # Amount patterns looks for currency symbols or just numbers at end of lines with keywords
        self.amount_pattern = re.compile(r'(?:Total|Grand Total|Amount|Net Payable)[:\s]*[Rs\.]?\s*([\d,]+\.?\d{0,2})', re.IGNORECASE)

    def extract_invoice_data(self, text):
        """
        Parse OCR text to extract structured invoice data.
        Returns a dictionary.
        """
        data = {
            "gst_number": None,
            "invoice_date": None,
            "total_amount": 0.0,
            "vendor_name": "Unknown Vendor",
            "raw_text": text
        }

        if not text:
            return data

        # 1. Extract GSTIN
        gst_match = self.gst_pattern.search(text)
        if gst_match:
            data["gst_number"] = gst_match.group(0)

        # 2. Extract Date (First valid date is assumed to be invoice date)
        date_matches = self.date_pattern.findall(text)
        if date_matches:
            # Simple normalizer check (placeholder)
            data["invoice_date"] = date_matches[0]

        # 3. Extract Total Amount
        # We take the largest number found associated with "Total" keywords
        amount_matches = self.amount_pattern.findall(text)
        if amount_matches:
            try:
                # Clean commas and convert to float, filter out bad parses
                amounts = [float(a.replace(',', '')) for a in amount_matches if a.replace(',', '').replace('.', '').isdigit()]
                if amounts:
                    data["total_amount"] = max(amounts) # Assumption: Grand total is usually the largest "Total"
            except:
                pass

        # 4. Vendor Name Heuristic
        # Usually the first line or lines before address.
        # This is hard with just regex, so we use a placeholder or the first non-empty line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            data["vendor_name"] = lines[0]

        return data
