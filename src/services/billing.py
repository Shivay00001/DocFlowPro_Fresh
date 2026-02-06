class BillingService:
    def calculate_gst(self, amount, tax_rate_percent, is_interstate=False):
        """
        Calculate GST breakdown.
        amount: Base amount or Total amount (simplification: assuming Base for now)
        """
        tax_amount = (amount * tax_rate_percent) / 100
        total = amount + tax_amount
        
        breakdown = {
            "taxable_value": amount,
            "tax_rate": tax_rate_percent,
            "tax_amount": tax_amount,
            "total_amount": total,
            "cgst": 0.0,
            "sgst": 0.0,
            "igst": 0.0
        }

        if is_interstate:
            breakdown["igst"] = tax_amount
        else:
            breakdown["cgst"] = tax_amount / 2
            breakdown["sgst"] = tax_amount / 2
            
        return breakdown

    def generate_summary(self, invoices):
        """
        Generate a summary report from a list of invoice dicts.
        """
        summary = {
            "total_revenue": 0.0,
            "total_tax": 0.0,
            "count": len(invoices)
        }
        
        for inv in invoices:
            summary["total_revenue"] += inv.get('total_amount', 0)
            # Assuming we store tax amount separately, if not, estimates
            summary["total_tax"] += inv.get('tax_amount', 0)
            
        return summary
