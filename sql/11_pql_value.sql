-- What are the unrouted product-qualified accounts worth?
-- Deal size: median closed-won amount for Pro and Business plan companies (enterprise excluded).
-- Lift: extra share of these accounts that would buy if sales worked them. This is a planning
-- assumption, shown at three levels; replace with the real conversion of worked PQLs once measured.
WITH deal_size AS (
    SELECT MEDIAN(d.amount) AS median_won_amount
    FROM deals d JOIN companies c USING (company_id)
    WHERE d.dealstage = 'closedwon' AND c.plan IN ('pro', 'business') AND d.amount IS NOT NULL
),
unrouted AS (
    SELECT COUNT(*) AS accounts
    FROM workspaces w JOIN companies co USING (company_id)
    WHERE w.active_users_30d >= 6 AND w.recordings_30d >= 25 AND co.owner_id IS NULL
      AND NOT EXISTS (SELECT 1 FROM deals d WHERE d.company_id = w.company_id
                      AND d.dealstage NOT IN ('closedwon', 'closedlost'))
),
lift AS (SELECT * FROM (VALUES (0.05), (0.10), (0.15)) t(extra_conversion))
SELECT u.accounts                                              AS unrouted_pql_accounts,
       s.median_won_amount,
       l.extra_conversion,
       ROUND(u.accounts * l.extra_conversion)                  AS extra_deals,
       ROUND(u.accounts * l.extra_conversion * s.median_won_amount) AS annual_value_at_stake
FROM unrouted u, deal_size s, lift l
ORDER BY l.extra_conversion;
