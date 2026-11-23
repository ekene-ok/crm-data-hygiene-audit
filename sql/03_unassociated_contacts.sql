-- Contacts with no company, even though their email domain matches a company already in the CRM.
-- These are missing from account views, routing and company-level reporting.
SELECT c.contact_id, c.email, co.company_id AS suggested_company_id, co.name AS suggested_company
FROM contacts c
JOIN companies co
  ON SPLIT_PART(LOWER(TRIM(c.email)), '@', 2) = co.domain
WHERE c.company_id IS NULL
ORDER BY c.contact_id;
