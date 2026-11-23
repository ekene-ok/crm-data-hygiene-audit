# 02. Cleanup Plan

Ordered by revenue impact first, then by effort. "Fix" cleans what exists; "Prevent" stops it coming back. Owners are roles, since Ferncast is fictional.

## Week 1: routing (highest revenue impact)

| Issue | Fix | Prevent | Owner |
|---|---|---|---|
| 158 MQLs with no owner | Assign in bulk to sales reps by territory | MQL assignment workflow (W-01) | RevOps |
| 254 MQLs past SLA | Send the list to sales managers for same-week follow-up | SLA alert workflow (W-02) and a weekly SLA report by rep | RevOps, Sales managers |
| 93 product-qualified accounts with no owner | Review the list with the sales lead and assign the top accounts by active users | PQL flag and routing workflow (W-03) | RevOps, Sales lead |
| 200 SQLs and opportunities with no owner | Assign to the owner of the associated company, or rotate | Include in W-01 | RevOps |

## Week 2: pipeline and forecast

| Issue | Fix | Prevent | Owner |
|---|---|---|---|
| 102 stale open deals ($2.48M) | Ask each owner to update the close date or close the deal out | Stale deal alert workflow (W-04) | Sales managers |
| 31 deals with no amount | Owners add amounts | Require Amount when a deal moves into a stage (pipeline settings) | RevOps |

## Weeks 3 to 4: data foundations

| Issue | Fix | Prevent | Owner |
|---|---|---|---|
| 269 likely duplicate contacts | Review in HubSpot's duplicates tool; merge confirmed pairs, keeping the record with the work email | Custom duplicate rule on first name, last name and company | RevOps |
| 72 duplicate companies | Merge subdomain records into the main domain record | Review company records created from subdomains weekly | RevOps |
| 379 contacts not linked to their company | Associate in bulk using the suggested company in the audit results | Turn on automatic company association, with freemail domains excluded | RevOps |
| 565 contacts with no lead source | Backfill from original source where possible | Required hidden field on every form; set source on product signups at creation | Marketing Ops |
| 57 "customer" contacts with no purchase | Clear lifecycle stage, then set the correct stage (W-05) | Set "customer" only from a closed-won deal or a paid plan | RevOps |

## Ongoing: keep it clean

- Run the ten checks in [sql/](../sql/) weekly and track each rate over time
- Share a one-page data health report with sales and marketing leadership each month
- Review every new integration for which fields it writes and whether it can create duplicates before turning it on

## Targets after 30 days

| Check | Now | Target |
|---|---|---|
| MQLs contacted within 24 hours | 31.5% | 80% |
| Product-qualified accounts with an owner | 33.1% | 95% |
| Open deals that are stale | 45.9% | Under 15% |
| SQLs and opportunities with no owner | 17.4% | 0% |
| Contacts with no lead source | 8.3% | Under 2% (new contacts: 0%) |
