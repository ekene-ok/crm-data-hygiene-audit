# 03. Proposed HubSpot Workflows

Specs for the automations in the [cleanup plan](02_cleanup_plan.md). These are designs, written against HubSpot's documented features; they have not been built in a live account. Subscription notes are included where a feature depends on the plan.

## W-01: MQL assignment

| | |
|---|---|
| **Object** | Contact |
| **Trigger** | Lifecycle stage becomes Marketing Qualified Lead **and** Contact owner is unknown |
| **Actions** | 1. If the associated company has an owner, copy the company owner to the contact. 2. Otherwise, use **Rotate record to owner** to assign a sales rep. 3. Send the owner an internal notification with the contact, company and lead source |
| **Requirements** | Rotate record to owner needs Sales Hub Professional or Enterprise, and only assigns users with a paid Sales seat |
| **Success measure** | MQLs with no owner: 0 |

## W-02: MQL follow-up SLA alert

| | |
|---|---|
| **Object** | Contact |
| **Trigger** | Lifecycle stage becomes Marketing Qualified Lead |
| **Actions** | 1. Delay 24 hours. 2. If there is no logged call, email or meeting since the MQL date, create a task for the owner and notify their manager. 3. Delay another 24 hours and repeat the check, then flag the contact for the weekly SLA report |
| **Success measure** | MQLs contacted within 24 hours: 80% or more |

## W-03: product-qualified account flag and routing

| | |
|---|---|
| **Object** | Company |
| **Depends on** | Product usage synced to company properties daily (active users and recordings in the last 30 days). This needs a product data sync, which is the first thing to confirm with Engineering |
| **Trigger** | Active users (30 days) is 6 or more **and** recordings (30 days) is 25 or more **and** plan is Free, Creator or Pro |
| **Actions** | 1. Set "Product qualified" to Yes and stamp the date. 2. If the company has no owner, rotate it to a sales rep. 3. Create a task: "Product-qualified account: review usage and reach out within 2 business days" |
| **Success measure** | Product-qualified accounts with an owner: 95% or more |
| **Review** | Check the thresholds after 60 days against which flagged accounts actually upgraded, and adjust |

## W-04: stale deal alert

| | |
|---|---|
| **Object** | Deal |
| **Trigger** | Deal is open **and** (close date is in the past **or** last activity date is more than 30 days ago) |
| **Actions** | 1. Create a task for the deal owner to update the close date or close the deal. 2. If unchanged after 7 days, notify the sales manager |
| **Success measure** | Stale open deals under 15% |

## W-05: lifecycle stage correction

| | |
|---|---|
| **Object** | Contact |
| **Trigger** | Manual enrollment from the audit list (contacts marked "customer" at free-plan companies with no closed-won deal) |
| **Actions** | 1. Clear the Lifecycle stage property. 2. Set Lifecycle stage to Lead (or Opportunity if there is an open deal) |
| **Why two steps** | HubSpot only moves lifecycle stages forward automatically; a workflow has to clear the value before setting an earlier stage |
| **Watch out for** | Clearing the stage resets the "Became a ... date" properties, which feed some default reports. Export those dates first |

## Settings changes (no workflow needed)

| Setting | Change | Note |
|---|---|---|
| Automatic company association | Turn on "Create and associate companies with contacts" | Exclude freemail domains. HubSpot creates a company per unique domain, including subdomains, so watch for new subdomain duplicates |
| Duplicate rules | Add a custom rule matching first name, last name and associated company | Bulk merging needs Data Hub Professional or Enterprise; review pairs before merging |
| Deal stage requirements | Require Amount and Close date when a deal moves into "Qualified to buy" and later stages | Not enforced on deal creation, so W-04 and the weekly checks still matter |
