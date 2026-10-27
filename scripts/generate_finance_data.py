"""Generate the Caldova Finance demo data: supplier invoices checked against the contract database, by country.

Story (invoice data to Friday 23 Oct 2026; "last 4 weeks" = 28 Sep - 23 Oct 2026):
  - Caldova has six European affiliates. Each signs its own supply contracts and receives invoices from the same ten
    suppliers, most of them weekly; Annterra Pharma ships and invoices finished packs every working day. Accounts Payable
    checks every invoice line against the contract price registered in the contract database and the goods receipt.
  - On 18 Sep 2026 Caldova Germany signed Amendment No. 1 with Annterra Pharma: $4.45 instead of $3.95 per pack from
    Monday 5 Oct 2026, in exchange for priority production slots. The request to register the new price went to
    a contract-admin mailbox that had closed on 15 Sep, so the contract database still holds $3.95. Since 5 Oct every
    German Annterra invoice is billed correctly but flagged "Price above contract": three weeks, 15 invoices, about
    $17K. With Net 30 terms the first ones fall due in the next payment run, and Accounts Payable wants to block them.
    The data can't tell that the invoices are right: only the work context (signed amendment, emails) can.
  - Nothing else is wrong in Germany in the last weeks. The other countries have the usual small, genuine errors, so
    the check itself works as designed.
  - Colin Ballinger (Country Manager, Germany) sees only Germany (RLS); Isaac Fielder (Region Manager, Europe) sees all.

Modes:
  default            the demo state: amendment signed but not registered (Germany's accuracy drops for three weeks).
  --registered       the state after the analytics team registers the amended price (used by
                     scripts/deploy/update_contract_price.py; write it to a separate folder with --out).

Outputs <out>/*.csv, _schema.json (Delta column types) and expected_answers.json (used by
scripts/deploy/deploy_finance.py validate and the demo script). Deterministic, except the registration date.
User principal names are written as <alias>@{{TENANT_DOMAIN}}; the deployment replaces the placeholder with the
tenant domain from config/tenant.json, so the committed data never holds a real tenant.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import pathlib
import random
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "finance"
TENANT_TOKEN = "{{TENANT_DOMAIN}}"  # deploy_finance.py replaces it with tenantDomain from config/tenant.json at load time
# Only user aliases and the story country are read: config/tenant.json if present, else the committed example
CFG = json.loads(next(p for p in (ROOT / "config" / "tenant.json", ROOT / "config" / "tenant.example.json")
                      if p.exists()).read_text(encoding="utf-8"))

AS_OF = dt.date(2026, 10, 23)  # Friday: the invoice data runs to this date
START = dt.date(2025, 1, 1)
DATE_END = dt.date(2026, 12, 31)
WEEK0 = AS_OF - dt.timedelta(days=AS_OF.weekday())  # Monday of the latest week (Weeks Ago = 0)
LAST_4W = (WEEK0 - dt.timedelta(weeks=3), AS_OF)  # 28 Sep - 23 Oct 2026
PREV_4W = (WEEK0 - dt.timedelta(weeks=7), WEEK0 - dt.timedelta(weeks=3, days=1))  # 31 Aug - 27 Sep 2026
TREND_WEEKS = 16
RECOVERED_BEFORE = AS_OF - dt.timedelta(weeks=6)  # older errors were caught and recovered as usual
NOISE_UNTIL = PREV_4W[0]  # random genuine errors only before the last 8 weeks; recent ones are planted below
NOISE_RATE = 0.012
CENT, MIL = Decimal("0.01"), Decimal("0.0001")

COUNTRIES = [  # id, country, ISO code, region, size factor
    (1, "Germany", "DE", "Europe", 1.4),
    (2, "France", "FR", "Europe", 1.1),
    (3, "Italy", "IT", "Europe", 0.9),
    (4, "Spain", "ES", "Europe", 0.8),
    (5, "United Kingdom", "GB", "Europe", 1.0),
    (6, "Switzerland", "CH", "Europe", 0.7),
]
# key, supplier id (stable IDs), code, name, category, line label, unit,
# contract price (USD), quantity per week for a size-1.0 country, rounding, payment terms (days),
# invoice weekdays (0 = Monday), invoice every n weeks
SUPPLIERS = [
    ("ANN", 1, "CM-001", "Annterra Pharma", "Contract Manufacturing (OSD)", "Finished packs, oral solid dose", "pack",
     "3.95", 8200, 50, 30, (0, 1, 2, 3, 4), 1),
    ("MDX", 3, "CM-003", "Meridax Life Sciences", "Contract Manufacturing (OSD)", "Finished packs, oral solid dose",
     "pack", "5.10", 4600, 100, 60, (2,), 1),
    ("QUO", 8, "API-001", "Quorvane Chemicals", "Active Pharmaceutical Ingredients", "Active pharmaceutical ingredient",
     "kg", "1850.00", 23, 1, 60, (0,), 1),
    ("LUM", 10, "EXC-001", "Lumexa Excipients", "Excipients", "Excipients", "kg", "12.50", 920, 20, 45, (3,), 1),
    ("PAK", 11, "PKG-001", "Pakvora Packaging", "Packaging", "Blister foil and cartons", "thousand units", "38.00", 185,
     5, 60, (1,), 1),
    ("COR", 12, "PKG-002", "Corrindale Glass", "Packaging", "Glass vials", "thousand vials", "210.00", 46, 1, 60, (3,), 1),
    ("GLA", 13, "LOG-001", "Glacivo Cold Chain", "Cold Chain Logistics", "Cold chain shipments", "shipment", "1450.00",
     3.2, 1, 30, (4,), 1),
    ("ANA", 15, "LAB-001", "Analytra Labs", "Laboratory Services", "Release tests", "test", "420.00", 9, 1, 30, (2,), 1),
    ("STV", 14, "CMS-001", "Sterivon Fill-Finish", "Contract Manufacturing (Sterile)", "Sterile fill-finish batch",
     "batch", "64800.00", 1, 1, 60, (1,), 4),
    ("DOS", 16, "DEV-001", "Dosmira Devices", "Device Components", "Autoinjector components", "thousand units",
     "1150.00", 14, 1, 60, (2,), 1),
]
# Signed contract amendments: the supplier bills the amended price from the effective date. Unless --registered, the
# contract database was NOT updated, so the invoice check still compares against the original price.
AMENDMENTS = {("DE", "ANN"): (dt.date(2026, 10, 5), "4.45")}
AMENDMENT_SIGNED = dt.date(2026, 9, 18)
ERRORS = [  # id, error type, description, is error, sort order
    (0, "No error", "The invoice matches the contract price in the contract database and the delivered quantity, and "
                    "it is billed once.", "No", 1),
    (1, "Price above contract", "The unit price on the invoice is higher than the contract price in the contract "
                                "database.", "Yes", 2),
    (2, "Duplicate invoice", "The same delivery was invoiced again on a second invoice.", "Yes", 3),
    (3, "Billed more than delivered", "The invoiced quantity is higher than the quantity in the goods receipt.", "Yes",
     4),
]
ERR = {name: i for i, name, *_ in ERRORS}
# Genuine errors in the last 8 weeks, outside Germany: (country, supplier, Monday of the week) -> (error type, value)
# value = billed price (price above contract) or delivered share of the billed quantity (billed more than delivered)
PLANTED = {
    ("GB", "LUM", dt.date(2026, 9, 7)): ("Billed more than delivered", 0.95),
    ("FR", "ANA", dt.date(2026, 9, 28)): ("Billed more than delivered", 0.80),
    ("IT", "COR", dt.date(2026, 10, 5)): ("Billed more than delivered", 0.80),
    ("CH", "GLA", dt.date(2026, 10, 12)): ("Duplicate invoice", None),
    ("ES", "PAK", dt.date(2026, 10, 19)): ("Price above contract", "39.50"),
}


def money(v: Decimal) -> Decimal:
    return v.quantize(CENT, rounding=ROUND_HALF_UP)


def mondays(start: dt.date, end: dt.date) -> list[dt.date]:
    day = start - dt.timedelta(days=start.weekday())
    out = []
    while day <= end:
        out.append(day)
        day += dt.timedelta(weeks=1)
    return out


def quantity(rng: random.Random, per_invoice: float, rounding: int, day: dt.date) -> int:
    season = 1 + 0.04 * math.sin((day.month - 1) / 12 * 2 * math.pi)
    q = per_invoice * season * rng.gauss(1, 0.04)
    return max(rounding, int(round(q / rounding)) * rounding)


def contract_id(cid: int, index: int) -> int:
    return cid * 100 + index


def noise(rng: random.Random, key: str, code: str, day: dt.date) -> tuple[str, object] | None:
    """Genuine errors: random history before the last 8 weeks (never Annterra), planted ones after that."""
    week = day - dt.timedelta(days=day.weekday())
    if day >= NOISE_UNTIL:
        return PLANTED.get((code, key, week)) if day == week + dt.timedelta(days=dict(
            (s[0], s[11][0]) for s in SUPPLIERS)[key]) else None
    if key == "ANN" or rng.random() >= NOISE_RATE:
        return None
    pick = rng.random()
    if pick < 0.5:
        return "Billed more than delivered", rng.choice((0.90, 0.92, 0.95, 0.97))
    if pick < 0.85:
        return "Price above contract", rng.choice((1.01, 1.02, 1.03, 1.04))
    return "Duplicate invoice", None


def build_invoices(rng: random.Random, registered: bool) -> list[dict]:
    invoices: list[dict] = []
    weeks = mondays(START, AS_OF)
    for cid, _country, code, _region, size in COUNTRIES:
        for w, monday in enumerate(weeks):
            for index, (key, sid, _scode, _name, _cat, label, unit, price, weekly, rounding, terms, weekdays,
                        every) in enumerate(SUPPLIERS, start=1):
                if w % every:
                    continue
                for weekday in weekdays:
                    inv_date = monday + dt.timedelta(days=weekday)
                    if not START <= inv_date <= AS_OF:
                        continue
                    qty = 1 if key == "STV" else quantity(rng, weekly * size * every / len(weekdays), rounding, inv_date)
                    contract_price = Decimal(price)
                    billed_price, delivered, error = contract_price, qty, "No error"
                    amendment = AMENDMENTS.get((code, key))
                    amended = bool(amendment and inv_date >= amendment[0])
                    if amended:
                        billed_price = Decimal(amendment[1])  # correct under the signed amendment
                        if registered:
                            contract_price = billed_price
                        else:
                            error = "Price above contract"  # the database still holds the old price
                    else:
                        plan = noise(rng, key, code, inv_date)
                        if plan:
                            error, value = plan
                            if error == "Price above contract":
                                billed_price = (Decimal(value) if isinstance(value, str)
                                                else (contract_price * Decimal(str(value))).quantize(CENT))
                            elif error == "Billed more than delivered":
                                delivered = max(0, int(qty * value) if rounding == 1
                                                else int(round(qty * value / rounding)) * rounding)
                                if delivered >= qty:
                                    delivered = qty - rounding
                    number = f"{key}-{code}-{inv_date:%y%m%d}"
                    line = {"LineDescription": label, "UnitOfMeasure": unit, "BilledQuantity": Decimal(qty),
                            "DeliveredQuantity": Decimal(delivered), "BilledUnitPrice": billed_price.quantize(MIL),
                            "ContractUnitPrice": contract_price.quantize(MIL),
                            "BilledAmount": money(Decimal(qty) * billed_price),
                            "ContractAmount": money(Decimal(min(qty, delivered)) * contract_price),
                            "ErrorTypeID": ERR["No error"] if error == "Duplicate invoice" else ERR[error],
                            "Amended": amended and not registered}
                    invoices.append({"InvoiceNumber": number, "InvoiceDate": inv_date, "CountryID": cid,
                                     "SupplierID": sid, "ContractID": contract_id(cid, index), "Terms": terms,
                                     "line": line})
                    if error == "Duplicate invoice":  # the same delivery invoiced again a few days later
                        dup_date = min(inv_date + dt.timedelta(days=3), AS_OF)
                        dup = dict(line, LineDescription=f"{label} (same delivery as {number})",
                                   ContractAmount=Decimal("0.00"), ErrorTypeID=ERR["Duplicate invoice"])
                        invoices.append({"InvoiceNumber": number + "-R", "InvoiceDate": dup_date, "CountryID": cid,
                                         "SupplierID": sid, "ContractID": contract_id(cid, index), "Terms": terms,
                                         "line": dup})
    return invoices


def flatten(invoices: list[dict], rng: random.Random) -> list[dict]:
    rows = []
    for i, inv in enumerate(sorted(invoices, key=lambda x: (x["InvoiceDate"], x["CountryID"], x["InvoiceNumber"])), 1):
        x = inv["line"]
        due = inv["InvoiceDate"] + dt.timedelta(days=inv["Terms"])
        paid = due + dt.timedelta(days=rng.randint(-3, 2))
        is_paid = paid <= AS_OF
        over = max(x["BilledAmount"] - x["ContractAmount"], Decimal("0.00"))
        is_error = x["ErrorTypeID"] != ERR["No error"]
        recovered = is_error and inv["InvoiceDate"] < RECOVERED_BEFORE
        if not is_error:
            step = "None"
        elif recovered:
            step = "Recovered"
        else:
            step = "Claim credit note" if is_paid else "Block payment"
        rows.append({
            "InvoiceLineID": i, "InvoiceNumber": inv["InvoiceNumber"], "InvoiceDate": inv["InvoiceDate"],
            "DueDate": due, "PaidDate": paid if is_paid else None, "PaymentStatus": "Paid" if is_paid else "Not yet paid",
            "CountryID": inv["CountryID"], "SupplierID": inv["SupplierID"], "ContractID": inv["ContractID"],
            "ErrorTypeID": x["ErrorTypeID"], "LineDescription": x["LineDescription"], "UnitOfMeasure": x["UnitOfMeasure"],
            "BilledQuantity": x["BilledQuantity"], "DeliveredQuantity": x["DeliveredQuantity"],
            "BilledUnitPrice": x["BilledUnitPrice"], "ContractUnitPrice": x["ContractUnitPrice"],
            "BilledAmount": x["BilledAmount"], "ContractAmount": x["ContractAmount"], "OverbilledAmount": over,
            "RecoveredAmount": over if recovered else Decimal("0.00"),
            "RecoveryStatus": ("Recovered" if recovered else "Open") if is_error else "Not needed", "NextStep": step,
            "_amended": x["Amended"],
        })
    return rows


def build_dates() -> list[dict]:
    out, day = [], START
    while day <= DATE_END:
        q = (day.month - 1) // 3 + 1
        week_start = day - dt.timedelta(days=day.weekday())
        out.append({"Date": day, "Year": day.year, "Quarter": f"Q{q}", "YearQuarter": f"{day.year} Q{q}",
                    "MonthNumber": day.month, "MonthName": day.strftime("%b"), "YearMonth": day.strftime("%b %Y"),
                    "YearMonthNumber": day.year * 100 + day.month, "MonthStart": day.replace(day=1),
                    "WeekStart": week_start, "Week": week_start.strftime("%d %b"),
                    "WeeksAgo": (WEEK0 - week_start).days // 7})
        day += dt.timedelta(days=1)
    return out


SCHEMA = {
    "fin_date": [("Date", "date"), ("Year", "int64"), ("Quarter", "string"), ("YearQuarter", "string"),
                 ("MonthNumber", "int64"), ("MonthName", "string"), ("YearMonth", "string"),
                 ("YearMonthNumber", "int64"), ("MonthStart", "date"), ("WeekStart", "date"), ("Week", "string"),
                 ("WeeksAgo", "int64")],
    "fin_countries": [("CountryID", "int64"), ("Country", "string"), ("CountryCode", "string"), ("Region", "string")],
    "fin_suppliers": [("SupplierID", "int64"), ("SupplierCode", "string"), ("SupplierName", "string"),
                      ("SupplierCategory", "string")],
    "fin_contracts": [("ContractID", "int64"), ("ContractCode", "string"), ("ContractCountry", "string"),
                      ("ContractName", "string"), ("PricingUnit", "string"), ("ContractUnitPrice", "decimal4"),
                      ("PriceLastUpdated", "date"), ("PaymentTerms", "string"), ("StartDate", "date"),
                      ("EndDate", "date")],
    "fin_error_types": [("ErrorTypeID", "int64"), ("ErrorType", "string"), ("ErrorDescription", "string"),
                        ("IsError", "string"), ("SortOrder", "int64")],
    "fin_invoice_lines": [("InvoiceLineID", "int64"), ("InvoiceNumber", "string"), ("InvoiceDate", "date"),
                          ("DueDate", "date"), ("PaidDate", "date"), ("PaymentStatus", "string"), ("CountryID", "int64"),
                          ("SupplierID", "int64"), ("ContractID", "int64"), ("ErrorTypeID", "int64"),
                          ("LineDescription", "string"), ("UnitOfMeasure", "string"), ("BilledQuantity", "decimal4"),
                          ("DeliveredQuantity", "decimal4"), ("BilledUnitPrice", "decimal4"),
                          ("ContractUnitPrice", "decimal4"), ("BilledAmount", "decimal2"), ("ContractAmount", "decimal2"),
                          ("OverbilledAmount", "decimal2"), ("RecoveredAmount", "decimal2"),
                          ("RecoveryStatus", "string"), ("NextStep", "string")],
    "fin_security_country_access": [("UserPrincipalName", "string"), ("Country", "string")],
}


def write(tables: dict[str, list[dict]], out: pathlib.Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("fin_*.csv"):
        if old.stem not in tables:
            old.unlink()
    for name, rows in tables.items():
        cols = [c for c, _ in SCHEMA[name]]
        with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow({c: ("" if r.get(c) is None else r[c]) for c in cols})
    (out / "_schema.json").write_text(json.dumps(SCHEMA, indent=2), encoding="utf-8")


def within(r: dict, window: tuple[dt.date, dt.date]) -> bool:
    return window[0] <= r["InvoiceDate"] <= window[1]


def agg(sub: list[dict]) -> dict:
    f = lambda v: float(money(v))  # noqa: E731
    inv = {r["InvoiceNumber"] for r in sub}
    bad = {r["InvoiceNumber"] for r in sub if r["ErrorTypeID"] != ERR["No error"]}
    billed = sum((r["BilledAmount"] for r in sub), Decimal(0))
    over = sum((r["OverbilledAmount"] for r in sub), Decimal(0))
    by_error = {}
    for i, name, *_ in ERRORS[1:]:
        lines = [r for r in sub if r["ErrorTypeID"] == i]
        by_error[name] = {"overbilled_usd": f(sum((r["OverbilledAmount"] for r in lines), Decimal(0))),
                          "invoices": len({r["InvoiceNumber"] for r in lines})}
    return {"invoices": len(inv), "invoices_with_errors": len(bad),
            "invoice_accuracy_pct": round(100 * (len(inv) - len(bad)) / len(inv), 1) if inv else None,
            "invoiced_usd": f(billed), "overbilled_usd": f(over),
            "overbilling_pct": round(100 * float(over / billed), 1) if billed else None,
            "payments_to_block_usd": f(sum((r["BilledAmount"] for r in sub if r["NextStep"] == "Block payment"),
                                           Decimal(0))),
            "invoices_to_block": len({r["InvoiceNumber"] for r in sub if r["NextStep"] == "Block payment"}),
            "by_error_type": by_error,
            "suppliers_with_overbilling": len({r["SupplierID"] for r in sub if r["OverbilledAmount"] > 0})}


def summarize(rows: list[dict], countries: dict[int, str], suppliers: dict[int, str]) -> dict:
    f = lambda v: float(money(v))  # noqa: E731
    last = [r for r in rows if within(r, LAST_4W)]
    prev = [r for r in rows if within(r, PREV_4W)]

    def by(sub: list[dict], key: str, names: dict) -> dict:
        out: dict = defaultdict(Decimal)
        for r in sub:
            out[r[key]] += r["OverbilledAmount"]
        return {names[k]: f(v) for k, v in sorted(out.items(), key=lambda kv: -kv[1]) if v > 0}

    supplier_error: dict = defaultdict(Decimal)
    for r in last:
        if r["OverbilledAmount"] > 0:
            supplier_error[f"{suppliers[r['SupplierID']]} | {ERRORS[r['ErrorTypeID']][1]}"] += r["OverbilledAmount"]
    # the same weeks once the signed Annterra amendment is registered: those invoices are correct
    fixed = [dict(r, ErrorTypeID=ERR["No error"], OverbilledAmount=Decimal("0.00"), NextStep="None")
             if r["_amended"] else r for r in last]
    weekly = defaultdict(list)
    for r in rows:
        week = r["InvoiceDate"] - dt.timedelta(days=r["InvoiceDate"].weekday())
        if (WEEK0 - week).days // 7 < TREND_WEEKS:
            weekly[week.isoformat()].append(r)
    return {
        "last_4_weeks": agg(last), "previous_4_weeks": agg(prev),
        "last_4_weeks_overbilled_by_country": by(last, "CountryID", countries),
        "last_4_weeks_accuracy_by_country": {countries[c]: agg([r for r in last if r["CountryID"] == c])["invoice_accuracy_pct"]
                                             for c in sorted({r["CountryID"] for r in last})},
        "last_4_weeks_overbilled_by_supplier": by(last, "SupplierID", suppliers),
        "last_4_weeks_overbilled_by_supplier_and_error": {k: f(v) for k, v in sorted(supplier_error.items(),
                                                                                      key=lambda kv: -kv[1])},
        "last_4_weeks_after_registration": agg(fixed),
        "weekly_invoice_accuracy_pct": {k: agg(v)["invoice_accuracy_pct"] for k, v in sorted(weekly.items())},
        "weekly_overbilled_usd": {k: agg(v)["overbilled_usd"] for k, v in sorted(weekly.items())},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registered", action="store_true",
                    help="state after the analytics team registers the signed amendment in the contract database")
    ap.add_argument("--registered-on", type=dt.date.fromisoformat, default=dt.date.today(),
                    help="registration date shown as 'Price Last Updated' (default: today)")
    ap.add_argument("--out", type=pathlib.Path, default=OUT, help=f"output folder (default: {OUT.relative_to(ROOT)})")
    args = ap.parse_args()
    out: pathlib.Path = args.out.resolve()

    rng = random.Random(20261023)
    rows = flatten(build_invoices(rng, args.registered), rng)
    countries = {cid: name for cid, name, *_ in COUNTRIES}
    suppliers = {s[1]: s[3] for s in SUPPLIERS}
    users = {role: f"{alias}@{TENANT_TOKEN}" for role, alias in CFG["users"].items()}
    contracts = []
    for c in COUNTRIES:
        for i, s in enumerate(SUPPLIERS, start=1):
            price, updated = Decimal(s[7]), dt.date(2025, 1, 1)
            amendment = AMENDMENTS.get((c[2], s[0]))
            if amendment and args.registered:
                price, updated = Decimal(amendment[1]), args.registered_on
            contracts.append({"ContractID": contract_id(c[0], i), "ContractCode": f"CTR-{s[0]}-{c[2]}",
                              "ContractCountry": c[1], "ContractName": f"{s[3]} - Caldova {c[1]} supply agreement",
                              "PricingUnit": s[6], "ContractUnitPrice": price.quantize(MIL), "PriceLastUpdated": updated,
                              "PaymentTerms": f"Net {s[10]}", "StartDate": dt.date(2025, 1, 1),
                              "EndDate": dt.date(2027, 12, 31)})
    tables = {
        "fin_date": build_dates(),
        "fin_countries": [{"CountryID": c[0], "Country": c[1], "CountryCode": c[2], "Region": c[3]} for c in COUNTRIES],
        "fin_suppliers": [{"SupplierID": s[1], "SupplierCode": s[2], "SupplierName": s[3], "SupplierCategory": s[4]}
                          for s in SUPPLIERS],
        "fin_contracts": contracts,
        "fin_error_types": [{"ErrorTypeID": i, "ErrorType": n, "ErrorDescription": d, "IsError": e, "SortOrder": s}
                            for i, n, d, e, s in ERRORS],
        "fin_invoice_lines": rows,
        "fin_security_country_access": [{"UserPrincipalName": users["businessUser"], "Country": CFG["colinCountry"]}],
    }
    write(tables, out)
    germany = [r for r in rows if countries[r["CountryID"]] == CFG["colinCountry"]]
    effective, amended_price = AMENDMENTS[("DE", "ANN")]
    ann_id = next(s[1] for s in SUPPLIERS if s[0] == "ANN")
    ann = [r for r in germany if r["SupplierID"] == ann_id and r["InvoiceDate"] >= effective]
    unpaid = [r for r in ann if r["PaymentStatus"] == "Not yet paid"]
    due_next = [r for r in unpaid if r["DueDate"] <= AS_OF + dt.timedelta(days=14)]
    total = lambda sub, col: float(money(sum((r[col] for r in sub), Decimal(0))))  # noqa: E731
    expected = {
        "as_of": AS_OF.isoformat(), "last_4_weeks": f"{LAST_4W[0]:%d %b} - {LAST_4W[1]:%d %b %Y}",
        "previous_4_weeks": f"{PREV_4W[0]:%d %b} - {PREV_4W[1]:%d %b %Y}", "amendment_registered": args.registered,
        "windows": {"last_4_weeks": [d.isoformat() for d in LAST_4W],
                    "previous_4_weeks": [d.isoformat() for d in PREV_4W]},
        "personas": {users["regionManager"]: summarize(rows, countries, suppliers),
                     users["businessUser"]: summarize(germany, countries, suppliers)},
        "annterra_germany_amendment": {
            "contract_code": "CTR-ANN-DE", "signed": AMENDMENT_SIGNED.isoformat(), "effective": effective.isoformat(),
            "amended_price": float(amended_price), "original_price": 3.95, "payment_terms": "Net 30",
            "price_in_contract_database": float(next(c["ContractUnitPrice"] for c in contracts
                                                     if c["ContractCode"] == "CTR-ANN-DE")),
            "invoices_since_effective": len({r["InvoiceNumber"] for r in ann}),
            "packs": int(sum(r["BilledQuantity"] for r in ann)),
            "invoiced_usd": total(ann, "BilledAmount"),
            "flagged_as_overbilled_usd": total(ann, "OverbilledAmount"),
            "invoices_not_yet_paid": len({r["InvoiceNumber"] for r in unpaid}),
            "invoice_value_not_yet_paid_usd": total(unpaid, "BilledAmount"),
            "invoices_due_in_next_two_weeks": len({r["InvoiceNumber"] for r in due_next}),
            "invoice_value_due_in_next_two_weeks_usd": total(due_next, "BilledAmount"),
            "first_due_date": min(r["DueDate"] for r in ann).isoformat() if ann else None,
        },
    }
    (out / "expected_answers.json").write_text(json.dumps(expected, indent=2), encoding="utf-8")
    print(f"wrote {out}{' (amendment registered)' if args.registered else ''}: "
          + ", ".join(f"{k} {len(v)}" for k, v in tables.items()))
    for who, s in expected["personas"].items():
        lq, pq, fx = s["last_4_weeks"], s["previous_4_weeks"], s["last_4_weeks_after_registration"]
        print(f"{who}: accuracy prev 4w {pq['invoice_accuracy_pct']}% -> last 4w {lq['invoice_accuracy_pct']}% "
              f"({lq['invoices_with_errors']}/{lq['invoices']}), overbilled ${lq['overbilled_usd']:,.0f}, "
              f"to block ${lq['payments_to_block_usd']:,.0f} ({lq['invoices_to_block']}); "
              f"after registration: {fx['invoice_accuracy_pct']}%, ${fx['overbilled_usd']:,.0f}")
        print("   by country:", s["last_4_weeks_overbilled_by_country"])
        print("   accuracy by country:", s["last_4_weeks_accuracy_by_country"])
        print("   supplier|error:", s["last_4_weeks_overbilled_by_supplier_and_error"])
        print("   weekly accuracy:", list(s["weekly_invoice_accuracy_pct"].values()))
    print("Annterra Germany:", expected["annterra_germany_amendment"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
