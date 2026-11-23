-- Contacts marked "customer" whose company is on the free plan with no closed-won deal.
-- These inflate customer counts and exclude real prospects from sales and nurture.
SELECT c.contact_id, c.email, co.company_id, co.plan
FROM contacts c
JOIN companies co USING (company_id)
WHERE c.lifecycle_stage = 'customer'
  AND co.plan = 'free'
  AND NOT EXISTS (
      SELECT 1 FROM deals d WHERE d.company_id = co.company_id AND d.dealstage = 'closedwon'
  )
ORDER BY c.contact_id;
