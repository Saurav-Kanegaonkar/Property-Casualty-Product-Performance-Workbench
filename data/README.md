# Data Sources

All operating datasets in this repository are synthetic. They are modeled on common P&C insurance product structures, including state and product segmentation, earned and written premium, incurred losses, loss ratio, combined ratio, retention, filing work items, underwriting guideline exceptions, and automation review signals.

The data is not presented as real carrier performance. It is designed to support a defensible portfolio artifact for a regional property and casualty product analyst use case.

## Generated files

- `portfolio_monthly.csv`: 1,152 synthetic monthly state, line, territory, and segment rows.
- `underwriting_segments.csv`: 96 segment records with exposure, inspection, telematics, automation, and guideline fields.
- `filing_backlog.csv`: 24 synthetic rate, rule, form, and manual maintenance work items.
- `workflow_requirements.csv`: 8 business requirements connecting product needs to IT and operational partners.
- `analysis/outputs/product_action_queue.csv`: ranked product action priorities.
- `analysis/outputs/filing_readiness.csv`: ranked filing and product maintenance readiness.
- `analysis/outputs/automation_review_queue.csv`: ranked automated decisioning review flags.
