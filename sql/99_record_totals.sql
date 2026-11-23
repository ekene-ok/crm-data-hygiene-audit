-- Denominators for the scorecard: how many records each check looked at.
SELECT 'contacts'           AS population, COUNT(*) AS records FROM contacts
UNION ALL SELECT 'companies',               COUNT(*) FROM companies
UNION ALL SELECT 'unassociated_contacts',   COUNT(*) FROM contacts WHERE company_id IS NULL
UNION ALL SELECT 'customer_stage',          COUNT(*) FROM contacts WHERE lifecycle_stage = 'customer'
UNION ALL SELECT 'sales_stage',             COUNT(*) FROM contacts WHERE lifecycle_stage IN ('salesqualifiedlead', 'opportunity')
UNION ALL SELECT 'mqls',                    COUNT(*) FROM contacts WHERE lifecycle_stage = 'marketingqualifiedlead'
UNION ALL SELECT 'open_deals',              COUNT(*) FROM deals WHERE dealstage NOT IN ('closedwon', 'closedlost')
UNION ALL SELECT 'open_pipeline',           CAST(SUM(amount) AS BIGINT) FROM deals WHERE dealstage NOT IN ('closedwon', 'closedlost')
UNION ALL SELECT 'deals',                   COUNT(*) FROM deals
UNION ALL SELECT 'self_serve_workspaces',   COUNT(*) FROM workspaces;
