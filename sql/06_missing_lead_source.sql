-- Contacts with no lead source: they cannot be credited to a channel in pipeline reporting.
SELECT contact_id, email, lifecycle_stage, created_at
FROM contacts
WHERE lead_source IS NULL
ORDER BY contact_id;
