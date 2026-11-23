-- MQL follow-up against a 24-hour service level agreement (SLA).
-- Each MQL is placed in one bucket so the totals add up.
SELECT
    contact_id,
    email,
    became_mql_at,
    first_contacted_at,
    CASE
        WHEN owner_id IS NULL                                            THEN '1. No owner assigned'
        WHEN first_contacted_at IS NULL                                  THEN '2. Owner, never contacted'
        WHEN first_contacted_at > became_mql_at + INTERVAL 24 HOUR       THEN '3. Contacted after 24 hours'
        ELSE                                                                  '4. Contacted within 24 hours'
    END AS follow_up_status
FROM contacts
WHERE lifecycle_stage = 'marketingqualifiedlead'
ORDER BY contact_id;
