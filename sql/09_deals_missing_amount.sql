-- Deals with no amount: they are left out of pipeline value and forecast totals.
SELECT deal_id, company_id, dealstage, owner_id
FROM deals
WHERE amount IS NULL
ORDER BY deal_id;
