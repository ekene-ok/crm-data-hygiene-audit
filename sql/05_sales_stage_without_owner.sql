-- Sales-qualified leads and opportunities with no contact owner: nobody is accountable for follow-up.
SELECT contact_id, email, lifecycle_stage, company_id
FROM contacts
WHERE lifecycle_stage IN ('salesqualifiedlead', 'opportunity')
  AND owner_id IS NULL
ORDER BY contact_id;
