-- Synthetic portfolio QA checks for the P&C product performance workbench.

-- Check 1: portfolio rows should have positive earned premium and non-negative losses.
select
  count(*) as invalid_rows
from portfolio_monthly
where earned_premium <= 0
   or incurred_losses < 0;

-- Check 2: segment keys should be unique in the segment table.
select
  segment_id,
  count(*) as row_count
from underwriting_segments
group by segment_id
having count(*) > 1;

-- Check 3: monthly metrics should reconcile to a plausible ratio range.
select
  segment_id,
  month,
  loss_ratio,
  combined_ratio
from portfolio_monthly
where loss_ratio < 0
   or combined_ratio < loss_ratio
   or combined_ratio > 160;

-- Check 4: filing work items should have an owner and status.
select
  state,
  product_line
from filing_backlog
where owner is null
   or filing_status is null;

-- Check 5: automation review queue should prioritize high exposure or workflow risk.
select
  segment_id,
  review_score,
  exposure_index,
  inspection_completion,
  guideline_exception_rate
from automation_review_queue
where review_score >= 70
  and exposure_index < 40
  and inspection_completion > 85
  and guideline_exception_rate < 20;
