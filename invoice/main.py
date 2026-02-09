import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f)


def create_invoice(config_path: str, output_path: str):
    config = load_config(config_path)

    sender = config["sender"]
    client = config["client"]
    payment = config["payment"]
    inv = config["invoice"]
    line_items = config["line_items"]

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Colors
    dark_gray = HexColor("#333333")
    medium_gray = HexColor("#666666")
    light_gray = HexColor("#CCCCCC")

    # Header - INVOICE title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(dark_gray)
    c.drawString(50, height - 60, "INVOICE")

    # Invoice details (right side)
    c.setFont("Helvetica", 10)
    c.setFillColor(medium_gray)
    c.drawRightString(width - 50, height - 40, f"Invoice #: {inv['number']}")
    c.drawRightString(width - 50, height - 55, f"Date: {inv['date']}")
    c.drawRightString(width - 50, height - 70, f"Due Date: {inv['due_date']}")
    c.drawRightString(width - 50, height - 85, f"Terms: {inv['terms']}")

    # Horizontal line
    c.setStrokeColor(light_gray)
    c.setLineWidth(1)
    c.line(50, height - 105, width - 50, height - 105)

    # FROM section
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(medium_gray)
    c.drawString(50, height - 130, "FROM")

    c.setFont("Helvetica", 10)
    c.setFillColor(dark_gray)
    c.drawString(50, height - 145, sender["name"])
    c.drawString(50, height - 158, sender["address_line1"])
    c.drawString(50, height - 171, sender["address_line2"])
    c.drawString(50, height - 184, sender["email"])

    # TO section
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(medium_gray)
    c.drawString(300, height - 130, "TO")

    c.setFont("Helvetica", 10)
    c.setFillColor(dark_gray)
    c.drawString(300, height - 145, client["name"])
    c.drawString(300, height - 158, client["address_line1"])
    c.drawString(300, height - 171, client["address_line2"])
    c.drawString(300, height - 184, f"Attn: {client['attention']}")

    # Table header
    table_top = height - 240
    c.setFillColor(HexColor("#F5F5F5"))
    c.rect(50, table_top - 5, width - 100, 25, fill=True, stroke=False)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(dark_gray)
    c.drawString(60, table_top + 5, "Description")
    c.drawRightString(width - 60, table_top + 5, "Amount")

    # Table content
    c.setFont("Helvetica", 10)
    c.setFillColor(dark_gray)

    # Calculate total and render line items
    total = 0
    desc_y = table_top - 30

    for item in line_items:
        # Render description lines
        for i, line in enumerate(item["description"]):
            c.drawString(60, desc_y - (i * 15), line)

        # Render amount (vertically centered with description)
        amount = item["amount"]
        total += amount
        amount_y = desc_y - ((len(item["description"]) - 1) * 15) / 2
        c.drawRightString(width - 60, amount_y, f"${amount:,.2f}")

        # Move down for next item
        desc_y -= (len(item["description"]) * 15) + 20

    # Line above total
    total_y = desc_y - 20
    c.setStrokeColor(light_gray)
    c.line(350, total_y, width - 50, total_y)

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, total_y - 25, "Total Due:")
    c.drawRightString(width - 60, total_y - 25, f"${total:,.2f}")

    # Payment section
    payment_y = total_y - 90
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(dark_gray)
    c.drawString(50, payment_y, "Payment Information")

    c.setStrokeColor(light_gray)
    c.line(50, payment_y - 10, width - 50, payment_y - 10)

    c.setFont("Helvetica", 10)
    c.setFillColor(medium_gray)
    c.drawString(
        50, payment_y - 30, "Please make payment via one of the following methods:"
    )

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, payment_y - 55, "ACH Transfer:")
    c.setFont("Helvetica", 10)
    c.drawString(70, payment_y - 70, f"Account Number: {payment['ach_account_number']}")
    c.drawString(70, payment_y - 85, f"Routing Number: {payment['ach_routing_number']}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, payment_y - 110, "Check:")
    c.setFont("Helvetica", 10)
    c.drawString(70, payment_y - 125, f"Payable to {payment['check_payable_to']}")

    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColor(light_gray)
    c.drawCentredString(width / 2, 50, "Thank you for your business")

    c.save()


# uv run invoice/main.py invoice/config.json ~/Documents/consulting/xyz.pdf
if __name__ == "__main__":
    import sys

    config_file = sys.argv[1] if len(sys.argv) > 1 else "invoice/config.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "invoice.pdf"

    create_invoice(config_file, output_file)
    print(f"Invoice created: {output_file}")
