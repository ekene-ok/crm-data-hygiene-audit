-- Likely duplicate companies: the same company name stored under more than one domain.
-- HubSpot creates a separate company for each unique domain, including subdomains
-- (example.com and app.example.com become two records).
-- Returns the extra records (the oldest record in each group is kept).
SELECT company_id, name, domain, created_at
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY LOWER(name) ORDER BY created_at) AS rn
    FROM companies
)
WHERE rn > 1
ORDER BY name, created_at;
