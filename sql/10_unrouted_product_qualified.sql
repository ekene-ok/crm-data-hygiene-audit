-- Product-qualified accounts nobody in sales is working.
-- Signal: 6+ active users and 25+ recordings in the last 30 days on a self-serve plan,
-- with no company owner and no open deal.
SELECT
    w.workspace_id, w.company_id, co.name, w.plan,
    w.active_users_30d, w.recordings_30d, w.invites_sent_30d
FROM workspaces w
JOIN companies co USING (company_id)
WHERE w.active_users_30d >= 6
  AND w.recordings_30d >= 25
  AND co.owner_id IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM deals d
      WHERE d.company_id = w.company_id
        AND d.dealstage NOT IN ('closedwon', 'closedlost')
  )
ORDER BY w.active_users_30d DESC, w.workspace_id;
