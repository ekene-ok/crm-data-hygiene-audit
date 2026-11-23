-- Likely duplicate contacts: same first and last name at the same company, under different emails.
-- HubSpot already merges exact email matches, so these are the duplicates it does not catch,
-- usually a personal email used for a product signup. Treat as candidates to review, not auto-merge.
-- Returns the extra records (the oldest record in each group is kept).
SELECT contact_id, email, first_name, last_name, company_id, created_at
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY LOWER(first_name), LOWER(last_name), company_id ORDER BY created_at) AS rn
    FROM contacts
    WHERE company_id IS NOT NULL
)
WHERE rn > 1
ORDER BY company_id, last_name, first_name, created_at;
