"""Run the CRM hygiene checks: detail files to results/, scorecard, and charts to images/.

Run: python src/run_analysis.py   (generates the synthetic data first if needed)
"""
from pathlib import Path
import sys
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, SQL, RES, IMG = ROOT / "data", ROOT / "sql", ROOT / "results", ROOT / "images"
HIGHLIGHT, GREY, INK, MUTED = "#0f7c90", "#c9c7c1", "#1a1a1a", "#6b6a66"

CHECKS = [
    # file stem, area, label, denominator, what it breaks
    ("01_duplicate_contacts", "Duplicates", "Duplicate contacts", "contacts", "Double-counted leads, emails sent twice, split activity history"),
    ("02_duplicate_companies", "Duplicates", "Duplicate companies", "companies", "Two owners on one account, broken account reporting"),
    ("03_unassociated_contacts", "Associations", "Contacts not linked to their company", "contacts", "Missing from account views, routing and company reporting"),
    ("04_customer_stage_without_purchase", "Lifecycle", "'Customer' with no purchase", "customer_stage", "Inflated customer counts; real prospects excluded from sales"),
    ("05_sales_stage_without_owner", "Ownership", "SQLs and opportunities with no owner", "sales_stage", "Nobody accountable for follow-up"),
    ("06_missing_lead_source", "Required fields", "Contacts with no lead source", "contacts", "Pipeline cannot be credited to a channel"),
    ("07_mql_follow_up", "Routing", "MQLs not contacted within 24 hours", "mqls", "Slower follow-up, lower conversion"),
    ("08_stale_open_deals", "Pipeline", "Stale open deals", "open_deals", "Forecast includes pipeline nobody is working"),
    ("09_deals_missing_amount", "Required fields", "Deals with no amount", "deals", "Left out of pipeline value and forecast"),
    ("10_unrouted_product_qualified", "Routing", "Product-qualified accounts with no sales owner", None, "Expansion revenue left to chance"),
]


def load():
    if not (DATA / "contacts.csv").exists():
        sys.path.insert(0, str(Path(__file__).parent))
        import generate_data
        generate_data.main()
    con = duckdb.connect()
    for t in ["companies", "contacts", "deals", "workspaces"]:
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{DATA / (t + '.csv')}')")
    return con


def scorecard(con):
    RES.mkdir(exist_ok=True)
    totals = dict(con.execute((SQL / "99_record_totals.sql").read_text()).fetchall())
    heavy = con.execute("SELECT COUNT(*) FROM workspaces WHERE active_users_30d >= 6 AND recordings_30d >= 25").fetchone()[0]
    rows, details = [], {}
    for stem, area, label, denom, why in CHECKS:
        df = con.execute((SQL / f"{stem}.sql").read_text()).df()
        df.to_csv(RES / f"{stem}.csv", index=False)
        details[stem] = df
        n = len(df)
        if stem == "07_mql_follow_up":
            n = int((df.follow_up_status != "4. Contacted within 24 hours").sum())
        base = heavy if stem.startswith("10") else totals[denom]
        rows.append({"check": stem[:2], "area": area, "issue": label, "records_affected": n,
                     "records_checked": base, "rate_pct": round(100 * n / base, 1), "what_it_breaks": why})
    sc = pd.DataFrame(rows)
    sc.to_csv(RES / "scorecard.csv", index=False)
    stale = details["08_stale_open_deals"]
    extra = {
        "open_pipeline": totals["open_pipeline"],
        "stale_pipeline": int(stale.amount.sum()),
        "stale_deals": len(stale),
        "product_qualified_accounts": heavy,
        "unrouted_pqls": len(details["10_unrouted_product_qualified"]),
    }
    pd.Series(extra).to_csv(RES / "headline_numbers.csv", header=["value"])
    print(sc.drop(columns="what_it_breaks").to_string(index=False))
    print("\n", pd.Series(extra).to_string())
    print("\n", details["07_mql_follow_up"].follow_up_status.value_counts().sort_index().to_string())
    return sc, details, extra


def style(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0, labelsize=11, colors=INK)


def chart_mql(df):
    counts = df.follow_up_status.value_counts().sort_index()
    labels = [s.split(". ")[1] for s in counts.index][::-1]
    vals = counts.values[::-1]
    total = vals.sum()
    colors = [GREY if l.startswith("Contacted within") else (HIGHLIGHT if l.startswith("No owner") else GREY) for l in labels]
    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=150)
    bars = ax.barh(labels, vals, color=colors, height=0.6)
    for b, v in zip(bars, vals):
        ax.text(v + total * 0.01, b.get_y() + b.get_height() / 2, f"{v}  ({100 * v / total:.0f}%)", va="center", fontsize=10.5, color=INK)
    ax.set_xlim(0, max(vals) * 1.3)
    style(ax)
    fig.suptitle("Most late MQLs never had an owner to follow up", x=0.02, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.02, 0.86, f"Follow-up status of {total} MQLs against a 24-hour SLA", fontsize=10, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(IMG / "01_mql_follow_up.png", facecolor="white")
    plt.close(fig)


def chart_pql(extra):
    total, unrouted = extra["product_qualified_accounts"], extra["unrouted_pqls"]
    labels, vals = ["Being worked by sales", "No owner, no open deal"], [total - unrouted, unrouted]
    fig, ax = plt.subplots(figsize=(7.5, 3.0), dpi=150)
    bars = ax.barh(labels[::-1], vals[::-1], color=[HIGHLIGHT, GREY], height=0.55)
    for b, v in zip(bars, vals[::-1]):
        ax.text(v + total * 0.01, b.get_y() + b.get_height() / 2, f"{v}  ({100 * v / total:.0f}%)", va="center", fontsize=11, color=INK)
    ax.set_xlim(0, max(vals) * 1.3)
    style(ax)
    fig.suptitle("Most busy self-serve teams have nobody from sales talking to them", x=0.02, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.02, 0.82, f"{total} product-qualified accounts (6+ active users and 25+ recordings in 30 days)", fontsize=10, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.82))
    fig.savefig(IMG / "02_unrouted_product_qualified.png", facecolor="white")
    plt.close(fig)


def main():
    IMG.mkdir(exist_ok=True)
    sc, details, extra = scorecard(load())
    chart_mql(details["07_mql_follow_up"])
    chart_pql(extra)
    print("\ncharts saved to images/")


if __name__ == "__main__":
    main()
