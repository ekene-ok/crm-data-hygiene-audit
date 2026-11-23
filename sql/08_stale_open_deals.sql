-- Open deals that look abandoned: close date already passed, or no activity in 30 days.
-- This pipeline is still counted in forecasts.
SELECT
    deal_id, company_id, dealstage, amount, closedate, last_activity_at, owner_id,
    closedate < DATE '2026-11-20'                              AS close_date_passed,
    last_activity_at < DATE '2026-11-20' - INTERVAL 30 DAY     AS no_recent_activity
FROM deals
WHERE dealstage NOT IN ('closedwon', 'closedlost')
  AND (closedate < DATE '2026-11-20' OR last_activity_at < DATE '2026-11-20' - INTERVAL 30 DAY)
ORDER BY deal_id;
