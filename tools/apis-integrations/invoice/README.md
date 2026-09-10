# Invoice Generator

This directory contains the ReportLab script and JSON configuration used to generate consulting invoices.

## Generate the current invoice

From the repository root, run:

```bash
uv run python \
  tools/apis-integrations/invoice/main.py \
  tools/apis-integrations/invoice/config.json
```

With no output path, the script writes to `~/Documents/consulting/gun/jyablonski-gun-invoice-YYYYMMDD.pdf`, using the date in `config.json` for `YYYYMMDD`.

To send the PDF to a specific file location, pass that path as the optional second argument:

```bash
uv run python \
  tools/apis-integrations/invoice/main.py \
  tools/apis-integrations/invoice/config.json \
  /path/to/custom-invoice.pdf
```

## Create a new invoice

1. Open `config.json` and update `invoice.number`, `invoice.date`, `invoice.due_date`, and `invoice.terms`.
1. Update the line item description, service period, hours, and rate. Hours and rate are printed in their own invoice columns.
1. Set `line_items[].amount` to the matching hours × rate total.
1. Run the generation command above. The default filename will use the updated invoice date; provide a custom output path when needed.
1. Open the generated PDF and confirm the invoice number, dates, description, payment details, and total.

The config contains sensitive payment information. Keep it private and do not commit or share it publicly.
