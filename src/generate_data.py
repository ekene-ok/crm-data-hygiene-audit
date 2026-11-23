"""Generate a synthetic HubSpot-style CRM export for Ferncast.

Ferncast is a fictional video and podcast recording SaaS with a self-serve
product and a sales team for larger accounts. All records are simulated,
with known data quality problems planted at set rates so the audit can find them.
Run: python src/generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 11
SNAPSHOT = pd.Timestamp("2026-11-20")
OUT = Path(__file__).resolve().parents[1] / "data"
OWNERS = ["owner_01", "owner_02", "owner_03", "owner_04", "owner_05", "owner_06"]
FIRST = ["Amara", "Ben", "Chloe", "Dev", "Ema", "Farah", "Gabe", "Hana", "Ivan", "Jade", "Kofi", "Lena",
         "Marco", "Nia", "Omar", "Priya", "Quinn", "Rosa", "Sam", "Tara", "Uche", "Vera", "Wes", "Yara", "Zoe"]
LAST = ["Adeyemi", "Brooks", "Chen", "Diaz", "Evans", "Fischer", "Garcia", "Hughes", "Ito", "Jensen", "Khan",
        "Lopez", "Mensah", "Nguyen", "Okoro", "Patel", "Reyes", "Silva", "Tanaka", "Walsh"]
WORDS = ["north", "lumen", "oak", "pixel", "harbor", "signal", "cedar", "orbit", "maple", "studio", "river",
         "summit", "atlas", "nova", "echo", "granite", "willow", "beacon", "prism", "delta"]
SUFFIX = ["media", "labs", "group", "co", "studios", "digital", "works", "hq"]


def main():
    rng = np.random.default_rng(SEED)
    OUT.mkdir(exist_ok=True)

    # Companies
    n_co = 2400
    names, seen = [], set()
    while len(names) < n_co:
        nm = f"{rng.choice(WORDS)}{rng.choice(WORDS)}{rng.choice(SUFFIX)}"
        if nm not in seen:
            seen.add(nm); names.append(nm)
    plan = rng.choice(["free", "creator", "pro", "business", "enterprise"], n_co, p=[0.38, 0.27, 0.20, 0.11, 0.04])
    companies = pd.DataFrame({
        "company_id": [f"C{i:05d}" for i in range(n_co)],
        "name": [n.title() for n in names],
        "domain": [f"{n}.com" for n in names],
        "plan": plan,
        "country": rng.choice(["US", "CA", "UK", "DE", "AU", None], n_co, p=[0.45, 0.12, 0.15, 0.1, 0.08, 0.10]),
        "owner_id": np.where(np.isin(plan, ["business", "enterprise"]), rng.choice(OWNERS, n_co), None),
        "created_at": SNAPSHOT - pd.to_timedelta(rng.integers(30, 900, n_co), unit="D"),
    })

    # Duplicate companies (~3%): HubSpot creates one company per unique domain, including
    # subdomains, so a contact signing up from app.example.com creates a second record
    dup_src = companies.sample(frac=0.03, random_state=SEED)
    dups = dup_src.copy()
    dups["company_id"] = [f"C{i:05d}" for i in range(n_co, n_co + len(dups))]
    dups["domain"] = "app." + dups["domain"]
    dups["created_at"] = (dups.created_at + pd.to_timedelta(rng.integers(5, 200, len(dups)), unit="D")).clip(upper=SNAPSHOT)
    dups["owner_id"] = None
    companies = pd.concat([companies, dups], ignore_index=True)

    # Contacts
    base = companies.iloc[:n_co]
    per = np.where(np.isin(base.plan, ["business", "enterprise"]), rng.integers(3, 12, n_co), rng.integers(1, 4, n_co))
    rows = []
    for co, k, pl in zip(base.itertuples(), per, base.plan):
        for _ in range(k):
            f, l = rng.choice(FIRST), rng.choice(LAST)
            rows.append((co.company_id, f, l, f"{f}.{l}{rng.integers(1, 99)}@{co.domain}".lower(), pl))
    contacts = pd.DataFrame(rows, columns=["company_id", "first_name", "last_name", "email", "plan"])
    m = len(contacts)
    paid = contacts.plan.isin(["creator", "pro", "business", "enterprise"]).to_numpy()
    stage = np.where(paid, rng.choice(["customer", "opportunity", "salesqualifiedlead"], m, p=[0.8, 0.1, 0.1]),
                     rng.choice(["subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead"], m, p=[0.35, 0.4, 0.17, 0.08]))
    contacts["lifecycle_stage"] = stage
    contacts["lead_source"] = rng.choice(["product_signup", "organic_search", "paid_social", "webinar", "referral", "event"], m,
                                         p=[0.45, 0.2, 0.15, 0.08, 0.07, 0.05])
    contacts["created_at"] = SNAPSHOT - pd.to_timedelta(rng.integers(1, 700, m), unit="D")
    contacts["country"] = companies.set_index("company_id").loc[contacts.company_id, "country"].to_numpy()

    # Owners: sales stages should always have an owner
    sales_stage = np.isin(stage, ["salesqualifiedlead", "opportunity"])
    contacts["owner_id"] = np.where(sales_stage | (paid & (rng.random(m) < 0.3)), rng.choice(OWNERS, m), None)

    # MQL timing and first contact (SLA: 1 business day, simplified to 24 hours)
    is_mql = stage == "marketingqualifiedlead"
    mql_at = SNAPSHOT - pd.to_timedelta(rng.integers(1, 120, m), unit="D") - pd.to_timedelta(rng.integers(0, 24, m), unit="h")
    contacts["became_mql_at"] = pd.Series(mql_at).where(is_mql)
    lag_h = np.where(rng.random(m) < 0.62, rng.uniform(0.5, 22, m), rng.gamma(2.0, 40, m))
    contacted = rng.random(m) > 0.18
    contacts["owner_id"] = np.where(is_mql & (rng.random(m) < 0.65), rng.choice(OWNERS, m), contacts.owner_id)
    contacts["first_contacted_at"] = (contacts.became_mql_at + pd.to_timedelta(lag_h, unit="h")).where(
        is_mql & contacted & contacts.owner_id.notna())

    # Planted problems
    p = rng.random(m)
    contacts.loc[p < 0.09, "lead_source"] = None                                          # missing lead source
    drop_owner = sales_stage & (rng.random(m) < 0.14)
    contacts.loc[drop_owner, "owner_id"] = None                                           # sales-stage contact with no owner
    orphan = rng.random(m) < 0.06
    contacts.loc[orphan, "company_id"] = None                                             # not associated to its company
    wrong_cust = (~paid) & (rng.random(m) < 0.03)
    contacts.loc[wrong_cust, "lifecycle_stage"] = "customer"                              # 'customer' with nothing paid

    # Duplicate contacts (~4%): HubSpot merges exact email matches, so real duplicates are the
    # same person under a second address, usually a personal email used for a product signup
    d = contacts[contacts.company_id.notna()].sample(frac=0.04, random_state=SEED + 1).copy()
    d["email"] = [f"{f}.{l}{rng.integers(100, 999)}@{rng.choice(['gmail.com', 'outlook.com'])}".lower()
                  for f, l in zip(d.first_name, d.last_name)]
    d["lead_source"] = "product_signup"
    d["created_at"] = (d.created_at + pd.to_timedelta(rng.integers(1, 200, len(d)), unit="D")).clip(upper=SNAPSHOT)
    d["owner_id"] = None
    contacts = pd.concat([contacts, d], ignore_index=True)
    contacts.insert(0, "contact_id", [f"P{i:06d}" for i in range(len(contacts))])
    contacts = contacts.drop(columns="plan")

    # Deals (sales pipeline)
    deal_cos = base[np.isin(base.plan, ["pro", "business", "enterprise"])].sample(frac=0.55, random_state=SEED)
    k = len(deal_cos)
    dstage = rng.choice(["appointmentscheduled", "qualifiedtobuy", "presentationscheduled", "contractsent", "closedwon", "closedlost"],
                        k, p=[0.12, 0.14, 0.12, 0.10, 0.34, 0.18])
    is_open = ~np.isin(dstage, ["closedwon", "closedlost"])
    created = SNAPSHOT - pd.to_timedelta(np.where(is_open, rng.integers(5, 120, k), rng.integers(60, 400, k)), unit="D")
    close = created + pd.to_timedelta(rng.integers(30, 150, k), unit="D")
    # Most open deals are worked recently; about a third go quiet (planted)
    quiet = is_open & (rng.random(k) < 0.33)
    last_act = SNAPSHOT - pd.to_timedelta(np.where(quiet, rng.integers(31, 90, k), rng.integers(0, 20, k)), unit="D")
    last_act = np.maximum(last_act, created)
    amount = np.where(deal_cos.plan == "enterprise", rng.integers(30, 160, k) * 1000, rng.integers(3, 30, k) * 1000).astype(float)
    amount[rng.random(k) < 0.07] = np.nan                                                  # missing amount
    deals = pd.DataFrame({
        "deal_id": [f"D{i:05d}" for i in range(k)], "company_id": deal_cos.company_id.to_numpy(),
        "dealstage": dstage, "amount": amount, "createdate": created, "closedate": close,
        "last_activity_at": last_act, "owner_id": rng.choice(OWNERS, k),
    })

    # Product usage for self-serve workspaces (product-qualified signals)
    ws = base[np.isin(base.plan, ["free", "creator", "pro"])].copy()
    w = len(ws)
    heavy = rng.random(w) < 0.07
    # A minority of busy self-serve accounts already have a sales owner
    owned = ws.company_id.to_numpy()[heavy & (rng.random(w) < 0.3)]
    companies.loc[companies.company_id.isin(owned), "owner_id"] = rng.choice(OWNERS, len(owned))
    workspaces = pd.DataFrame({
        "workspace_id": [f"W{i:05d}" for i in range(w)], "company_id": ws.company_id.to_numpy(), "plan": ws.plan.to_numpy(),
        "active_users_30d": np.where(heavy, rng.integers(6, 25, w), rng.integers(1, 5, w)),
        "recordings_30d": np.where(heavy, rng.integers(25, 140, w), rng.integers(0, 20, w)),
        "invites_sent_30d": np.where(heavy, rng.integers(3, 20, w), rng.integers(0, 3, w)),
    })

    companies.to_csv(OUT / "companies.csv", index=False)
    contacts.to_csv(OUT / "contacts.csv", index=False)
    deals.to_csv(OUT / "deals.csv", index=False)
    workspaces.to_csv(OUT / "workspaces.csv", index=False)
    print(f"companies {len(companies):,}  contacts {len(contacts):,}  deals {len(deals):,}  workspaces {len(workspaces):,}")


if __name__ == "__main__":
    main()
