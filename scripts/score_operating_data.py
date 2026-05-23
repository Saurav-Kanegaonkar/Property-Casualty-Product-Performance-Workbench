import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
SRC = ROOT / "src"

random.seed(42)

states = [
    {"code": "WA", "name": "Washington", "rate_env": "moderate", "cat": 1.08},
    {"code": "OR", "name": "Oregon", "rate_env": "moderate", "cat": 1.04},
    {"code": "ID", "name": "Idaho", "rate_env": "light", "cat": 1.02},
    {"code": "CO", "name": "Colorado", "rate_env": "complex", "cat": 1.18},
    {"code": "CA", "name": "California", "rate_env": "complex", "cat": 1.26},
    {"code": "WY", "name": "Wyoming", "rate_env": "light", "cat": 1.10},
]

products = [
    {"line": "Home", "base_loss": 0.61, "expense": 0.29, "premium": 980000, "retention": 0.87},
    {"line": "Auto", "base_loss": 0.66, "expense": 0.25, "premium": 760000, "retention": 0.83},
    {"line": "Farm and Ranch", "base_loss": 0.70, "expense": 0.28, "premium": 540000, "retention": 0.89},
    {"line": "Umbrella", "base_loss": 0.47, "expense": 0.21, "premium": 190000, "retention": 0.91},
]

territories = [
    {"name": "Urban agency corridor", "geo": "urban", "risk": 0.96, "inspection": 0.92},
    {"name": "Rural farm belt", "geo": "rural", "risk": 1.06, "inspection": 0.84},
    {"name": "Wildland interface", "geo": "wildfire", "risk": 1.24, "inspection": 0.74},
    {"name": "Mountain and hail belt", "geo": "weather", "risk": 1.18, "inspection": 0.78},
]

months = [
    "2025-04",
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
]

owners = ["Product", "Underwriting", "Actuarial", "Claims", "IT", "Compliance"]
manual_sections = [
    "Eligibility",
    "Territory factors",
    "Protection class",
    "Deductible options",
    "Farm outbuilding coverage",
    "Telematics discount",
    "Inspection trigger",
    "Renewal review",
]


def money(value):
    return int(round(value, 0))


def clamp(value, low, high):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pct(value):
    return round(value * 100, 1)


def build_data():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(exist_ok=True)

    segments = []
    monthly = []
    filings = []
    requirements = []

    for s_idx, state in enumerate(states):
        for p_idx, product in enumerate(products):
            for t_idx, territory in enumerate(territories):
                seg_id = f"{state['code']}-{product['line'][:2].upper().replace('FA', 'FR')}-{t_idx + 1:02d}"
                state_load = state["cat"]
                product_load = product["base_loss"]
                territory_load = territory["risk"]
                exposure_index = clamp((state_load * territory_load - 0.85) * 100, 18, 92)
                automation_rate = clamp(0.72 - (exposure_index / 220) + random.uniform(-0.04, 0.05), 0.32, 0.88)
                guideline_exception_rate = clamp((exposure_index / 210) + random.uniform(0.02, 0.09), 0.06, 0.48)
                inspection_completion = clamp(territory["inspection"] - random.uniform(0.02, 0.12), 0.48, 0.96)
                telematics_eligible = clamp(0.28 + (0.22 if product["line"] == "Auto" else 0.05) + random.uniform(-0.04, 0.06), 0.05, 0.58)
                baseline_retention = clamp(product["retention"] - exposure_index / 500 + random.uniform(-0.025, 0.025), 0.68, 0.94)

                segments.append(
                    {
                        "segment_id": seg_id,
                        "state": state["code"],
                        "state_name": state["name"],
                        "product_line": product["line"],
                        "territory": territory["name"],
                        "geography_type": territory["geo"],
                        "rate_environment": state["rate_env"],
                        "exposure_index": round(exposure_index, 1),
                        "inspection_completion": pct(inspection_completion),
                        "telematics_eligible": pct(telematics_eligible),
                        "automation_approval_rate": pct(automation_rate),
                        "guideline_exception_rate": pct(guideline_exception_rate),
                        "baseline_retention": pct(baseline_retention),
                        "owner": owners[(s_idx + p_idx + t_idx) % len(owners)],
                    }
                )

                for m_idx, month in enumerate(months):
                    season = 1 + 0.07 * math.sin((m_idx / 12) * math.pi * 2)
                    trend = 1 + (m_idx - 5.5) * 0.006
                    written_premium = product["premium"] * state_load * (0.72 + random.random() * 0.48) * trend
                    earned_premium = written_premium * random.uniform(0.92, 1.02)
                    loss_ratio = clamp(
                        product_load * state_load * territory_load * season + random.uniform(-0.08, 0.10),
                        0.32,
                        1.28,
                    )
                    incurred_losses = earned_premium * loss_ratio
                    expense_ratio = clamp(product["expense"] + random.uniform(-0.025, 0.035), 0.17, 0.37)
                    combined_ratio = loss_ratio + expense_ratio
                    retention = clamp(baseline_retention + random.uniform(-0.035, 0.025), 0.62, 0.96)
                    policy_count = int((earned_premium / random.uniform(1250, 2400)) * (1.7 if product["line"] == "Umbrella" else 1.0))
                    claim_frequency = clamp(loss_ratio / random.uniform(7.5, 12.5), 0.02, 0.19)
                    avg_severity = incurred_losses / max(1, policy_count * claim_frequency)

                    monthly.append(
                        {
                            "month": month,
                            "segment_id": seg_id,
                            "state": state["code"],
                            "product_line": product["line"],
                            "territory": territory["name"],
                            "written_premium": money(written_premium),
                            "earned_premium": money(earned_premium),
                            "incurred_losses": money(incurred_losses),
                            "loss_ratio": pct(loss_ratio),
                            "expense_ratio": pct(expense_ratio),
                            "combined_ratio": pct(combined_ratio),
                            "retention": pct(retention),
                            "policy_count": policy_count,
                            "claim_frequency": pct(claim_frequency),
                            "avg_claim_severity": money(avg_severity),
                        }
                    )

    segment_rollups = {}
    for segment in segments:
        rows = [r for r in monthly if r["segment_id"] == segment["segment_id"]]
        earned = sum(r["earned_premium"] for r in rows)
        written = sum(r["written_premium"] for r in rows)
        losses = sum(r["incurred_losses"] for r in rows)
        avg_expense = sum(r["expense_ratio"] for r in rows) / len(rows)
        loss_ratio = (losses / earned) * 100
        combined_ratio = loss_ratio + avg_expense
        retention = sum(r["retention"] for r in rows) / len(rows)
        claim_frequency = sum(r["claim_frequency"] for r in rows) / len(rows)
        target_gap = combined_ratio - 94
        rate_indication = clamp((loss_ratio - 58) * 0.55 + (claim_frequency - 7.2) * 0.35, -6, 18)
        review_score = clamp(
            target_gap * 1.15
            + segment["exposure_index"] * 0.28
            + (100 - segment["inspection_completion"]) * 0.38
            + segment["guideline_exception_rate"] * 0.42
            - segment["automation_approval_rate"] * 0.12,
            0,
            100,
        )
        action_score = clamp(
            target_gap * 1.35
            + max(0, rate_indication) * 2.4
            + (86 - retention) * 1.15
            + segment["exposure_index"] * 0.12,
            0,
            100,
        )
        recommendation = "Monitor"
        if target_gap > 8 and rate_indication > 5:
            recommendation = "Prepare rate and rule filing"
        if segment["inspection_completion"] < 78 or segment["guideline_exception_rate"] > 27:
            recommendation = "Route to underwriting review"
        if target_gap > 14 and segment["geography_type"] in {"wildfire", "weather"}:
            recommendation = "Tighten guideline and inspection trigger"

        segment_rollups[segment["segment_id"]] = {
            **segment,
            "earned_premium": earned,
            "written_premium": written,
            "incurred_losses": losses,
            "loss_ratio": round(loss_ratio, 1),
            "combined_ratio": round(combined_ratio, 1),
            "retention": round(retention, 1),
            "claim_frequency": round(claim_frequency, 1),
            "target_gap": round(target_gap, 1),
            "rate_indication": round(rate_indication, 1),
            "review_score": round(review_score, 1),
            "action_score": round(action_score, 1),
            "recommendation": recommendation,
        }

    action_queue = sorted(segment_rollups.values(), key=lambda r: r["action_score"], reverse=True)[:24]
    automation_queue = sorted(segment_rollups.values(), key=lambda r: r["review_score"], reverse=True)[:24]

    for state in states:
        for product in products:
            rows = [r for r in segment_rollups.values() if r["state"] == state["code"] and r["product_line"] == product["line"]]
            earned = sum(r["earned_premium"] for r in rows)
            losses = sum(r["incurred_losses"] for r in rows)
            loss_ratio = losses / earned * 100
            combined_ratio = loss_ratio + sum(r["combined_ratio"] - r["loss_ratio"] for r in rows) / len(rows)
            rate_indication = clamp((combined_ratio - 92) * 0.62, -4, 16)
            proposed_change = round(clamp(rate_indication * 0.75, -3, 12), 1)
            complexity = "Low"
            if state["rate_env"] == "complex" or abs(proposed_change) > 6:
                complexity = "High"
            elif abs(proposed_change) > 3:
                complexity = "Medium"
            impacted = random.sample(manual_sections, 3)
            readiness = clamp(
                86
                - max(0, combined_ratio - 94) * 1.6
                - (9 if complexity == "High" else 3 if complexity == "Medium" else 0)
                + random.uniform(-4, 5),
                35,
                96,
            )
            filing_status = "Ready for actuarial review"
            if readiness < 58:
                filing_status = "Needs product owner decision"
            elif readiness < 72:
                filing_status = "Needs compliance packet"

            filings.append(
                {
                    "state": state["code"],
                    "product_line": product["line"],
                    "earned_premium": money(earned),
                    "loss_ratio": round(loss_ratio, 1),
                    "combined_ratio": round(combined_ratio, 1),
                    "rate_indication": round(rate_indication, 1),
                    "proposed_rate_change": proposed_change,
                    "filing_complexity": complexity,
                    "readiness_score": round(readiness, 1),
                    "filing_status": filing_status,
                    "manual_sections": "; ".join(impacted),
                    "form_or_rule_dependency": impacted[0],
                    "owner": owners[(len(filings) + 2) % len(owners)],
                }
            )

    req_templates = [
        ("Loss ratio monitor", "Create state and product alert when monthly loss ratio is 8 pts above rolling target.", "Product", "IT"),
        ("Inspection trigger", "Route property risks to review when exposure index is high and inspection completion is below target.", "Underwriting", "IT"),
        ("Filing packet tracker", "Expose manual sections, rate indication, proposed change, and compliance packet status in one view.", "Compliance", "Product"),
        ("Telematics adoption", "Identify auto segments where telematics eligibility is high but enrollment lags.", "Product", "Underwriting"),
        ("Farm outbuilding review", "Flag farm segments with severity movement and missing outbuilding documentation.", "Claims", "Underwriting"),
        ("Retention watchlist", "Rank profitable segments with retention pressure before rate changes are submitted.", "Product", "Actuarial"),
        ("Guideline exception QA", "Sample automated approvals where guideline exception rate exceeds threshold.", "Underwriting", "Compliance"),
        ("Implementation handoff", "Track product decision, actuarial support, IT requirement, and effective date readiness.", "Product", "IT"),
    ]
    for idx, template in enumerate(req_templates, 1):
        requirements.append(
            {
                "requirement_id": f"BR-{idx:03d}",
                "capability": template[0],
                "business_requirement": template[1],
                "requesting_team": template[2],
                "delivery_partner": template[3],
                "priority": "High" if idx in {1, 2, 3, 7} else "Medium",
                "status": ["Drafted", "Ready for sizing", "In review", "Accepted"][idx % 4],
            }
        )

    write_csv(
        DATA / "underwriting_segments.csv",
        segments,
        [
            "segment_id",
            "state",
            "state_name",
            "product_line",
            "territory",
            "geography_type",
            "rate_environment",
            "exposure_index",
            "inspection_completion",
            "telematics_eligible",
            "automation_approval_rate",
            "guideline_exception_rate",
            "baseline_retention",
            "owner",
        ],
    )
    write_csv(
        DATA / "portfolio_monthly.csv",
        monthly,
        [
            "month",
            "segment_id",
            "state",
            "product_line",
            "territory",
            "written_premium",
            "earned_premium",
            "incurred_losses",
            "loss_ratio",
            "expense_ratio",
            "combined_ratio",
            "retention",
            "policy_count",
            "claim_frequency",
            "avg_claim_severity",
        ],
    )
    write_csv(
        DATA / "filing_backlog.csv",
        filings,
        [
            "state",
            "product_line",
            "earned_premium",
            "loss_ratio",
            "combined_ratio",
            "rate_indication",
            "proposed_rate_change",
            "filing_complexity",
            "readiness_score",
            "filing_status",
            "manual_sections",
            "form_or_rule_dependency",
            "owner",
        ],
    )
    write_csv(
        DATA / "workflow_requirements.csv",
        requirements,
        [
            "requirement_id",
            "capability",
            "business_requirement",
            "requesting_team",
            "delivery_partner",
            "priority",
            "status",
        ],
    )

    action_fields = [
        "segment_id",
        "state",
        "product_line",
        "territory",
        "earned_premium",
        "loss_ratio",
        "combined_ratio",
        "retention",
        "target_gap",
        "rate_indication",
        "action_score",
        "recommendation",
        "owner",
    ]
    review_fields = [
        "segment_id",
        "state",
        "product_line",
        "territory",
        "geography_type",
        "exposure_index",
        "inspection_completion",
        "telematics_eligible",
        "automation_approval_rate",
        "guideline_exception_rate",
        "review_score",
        "recommendation",
    ]
    write_csv(OUTPUTS / "product_action_queue.csv", action_queue, action_fields)
    write_csv(OUTPUTS / "automation_review_queue.csv", automation_queue, review_fields)
    write_csv(
        OUTPUTS / "filing_readiness.csv",
        sorted(filings, key=lambda r: r["readiness_score"]),
        [
            "state",
            "product_line",
            "loss_ratio",
            "combined_ratio",
            "rate_indication",
            "proposed_rate_change",
            "filing_complexity",
            "readiness_score",
            "filing_status",
            "manual_sections",
            "owner",
        ],
    )

    portfolio_summary = {}
    for state in states:
        rows = [r for r in segment_rollups.values() if r["state"] == state["code"]]
        earned = sum(r["earned_premium"] for r in rows)
        losses = sum(r["incurred_losses"] for r in rows)
        portfolio_summary[state["code"]] = {
            "earnedPremium": earned,
            "lossRatio": round(losses / earned * 100, 1),
            "combinedRatio": round(sum(r["combined_ratio"] for r in rows) / len(rows), 1),
            "retention": round(sum(r["retention"] for r in rows) / len(rows), 1),
            "actionCount": len([r for r in rows if r["action_score"] >= 55]),
        }

    app_data = {
        "summary": {
            "earnedPremium": sum(r["earned_premium"] for r in segment_rollups.values()),
            "writtenPremium": sum(r["written_premium"] for r in segment_rollups.values()),
            "lossRatio": round(
                sum(r["incurred_losses"] for r in segment_rollups.values())
                / sum(r["earned_premium"] for r in segment_rollups.values())
                * 100,
                1,
            ),
            "combinedRatio": round(sum(r["combined_ratio"] for r in segment_rollups.values()) / len(segment_rollups), 1),
            "retention": round(sum(r["retention"] for r in segment_rollups.values()) / len(segment_rollups), 1),
            "segments": len(segment_rollups),
            "states": len(states),
            "filingItems": len(filings),
            "requirements": len(requirements),
        },
        "states": portfolio_summary,
        "actionQueue": action_queue[:12],
        "filingQueue": sorted(filings, key=lambda r: r["readiness_score"])[:12],
        "automationQueue": automation_queue[:12],
        "requirements": requirements,
        "productMix": [
            {
                "productLine": product["line"],
                "earnedPremium": sum(
                    r["earned_premium"] for r in segment_rollups.values() if r["product_line"] == product["line"]
                ),
                "combinedRatio": round(
                    sum(r["combined_ratio"] for r in segment_rollups.values() if r["product_line"] == product["line"])
                    / len([r for r in segment_rollups.values() if r["product_line"] == product["line"]]),
                    1,
                ),
            }
            for product in products
        ],
    }

    (SRC / "app_data.js").write_text(
        "window.workbenchData = " + json.dumps(app_data, indent=2) + ";\n",
        encoding="utf-8",
    )

    top = action_queue[0]
    filing_watch = sorted(filings, key=lambda r: r["readiness_score"])[0]
    review_top = automation_queue[0]
    (ROOT / "analysis" / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                "I generated and scored a synthetic regional P&C product portfolio across six Western states, four product lines, 96 underwriting segments, 1,152 monthly operating rows, 24 filing work items, and 8 business requirements.",
                "",
                "## Findings",
                "",
                f"- The highest priority product action is {top['segment_id']} in {top['state']} {top['product_line']}, with a {top['combined_ratio']}% combined ratio and {top['action_score']} action score.",
                f"- The lowest filing readiness item is {filing_watch['state']} {filing_watch['product_line']}, with {filing_watch['readiness_score']} readiness and {filing_watch['filing_status'].lower()}.",
                f"- The top underwriting automation review flag is {review_top['segment_id']}, driven by {review_top['exposure_index']} exposure index, {review_top['inspection_completion']}% inspection completion, and {review_top['guideline_exception_rate']}% guideline exception rate.",
                "",
                "## Recommendation",
                "",
                "Use the workbench as a product review packet: review adverse combined ratio movement, decide filing path, and route complex automated underwriting outcomes to targeted human review before scaling workflow automation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ROOT / "analysis" / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Generate synthetic monthly P&C portfolio metrics by state, product line, territory, and underwriting segment.",
                "2. Calculate loss ratio, combined ratio, retention, claim frequency, rate indication, and target gap.",
                "3. Rank product actions by combined ratio gap, rate need, retention pressure, and exposure index.",
                "4. Rank filing readiness by rate indication, regulatory complexity, manual sections impacted, and implementation status.",
                "5. Rank automated decisioning review by exposure index, inspection gaps, guideline exceptions, and automation approval rate.",
                "6. Convert the ranked outputs into a portfolio monitor, filing planner, and underwriting review queue.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ROOT / "data" / "README.md").write_text(
        "\n".join(
            [
                "# Data Sources",
                "",
                "All operating datasets in this repository are synthetic. They are modeled on common P&C insurance product structures, including state and product segmentation, earned and written premium, incurred losses, loss ratio, combined ratio, retention, filing work items, underwriting guideline exceptions, and automation review signals.",
                "",
                "The data is not presented as real carrier performance. It is designed to support a defensible portfolio artifact for a regional property and casualty product analyst use case.",
                "",
                "## Generated files",
                "",
                "- `portfolio_monthly.csv`: 1,152 synthetic monthly state, line, territory, and segment rows.",
                "- `underwriting_segments.csv`: 96 segment records with exposure, inspection, telematics, automation, and guideline fields.",
                "- `filing_backlog.csv`: 24 synthetic rate, rule, form, and manual maintenance work items.",
                "- `workflow_requirements.csv`: 8 business requirements connecting product needs to IT and operational partners.",
                "- `analysis/outputs/product_action_queue.csv`: ranked product action priorities.",
                "- `analysis/outputs/filing_readiness.csv`: ranked filing and product maintenance readiness.",
                "- `analysis/outputs/automation_review_queue.csv`: ranked automated decisioning review flags.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    return app_data


if __name__ == "__main__":
    data = build_data()
    print(f"Generated {data['summary']['segments']} segments")
    print(f"Portfolio combined ratio: {data['summary']['combinedRatio']}%")
    print(f"Top action: {data['actionQueue'][0]['segment_id']} {data['actionQueue'][0]['recommendation']}")
