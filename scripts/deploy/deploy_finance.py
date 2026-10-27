"""Deploy the Caldova Finance demo (supplier invoice assurance) to the tenant in config/tenant.json.

Steps (run in order; each is safe to re-run):
  workspaces   resolve (or create on the configured capacity) 'Caldova Finance' + 'Caldova Finance Insights' and the
               lakehouse LH_CaldovaFinance (schemas enabled). LaurenceG (Data Analyst, owns the data) Admin on both;
               the business users get no role on 'Caldova Finance', so model RLS applies to them: IsaacF (Region
               Manager Europe) Contributor and ColinB (Country Manager Germany) Viewer on 'Caldova Finance Insights'
  load         write data/finance/*.csv as Delta tables to OneLake (Tables/dbo/fin_*); other lakehouse tables stay.
               The {{TENANT_DOMAIN}} placeholder in the data is replaced with the configured tenant domain
  model        create the Direct Lake model 'Supplier Invoice Assurance' from fabric/ (TMDL). An existing model is
               left untouched unless --update-model is given (aborts if the service holds parts the repo doesn't)
  refresh      sync the lakehouse SQL analytics endpoint metadata and reframe the Direct Lake model
  connection   fixed identity: cloud connection that authenticates with the 'Caldova Finance' workspace identity,
               SSO off, so business users never need lakehouse access; model RLS still applies
  permissions  IsaacF and ColinB Read + Build (ReadExplore) on the model: the report in the Insights workspace, Fabric
               IQ in Microsoft 365 Copilot and Copilot Cowork (Build is needed for DAX queries)
  reports      publish the PBIR report 'Supplier Invoice Assurance' to 'Caldova Finance Insights', bound live to the
               model
  validate     DAX checks against data/finance/expected_answers.json (+ RLS impersonation once role members exist)

Never adds or removes RLS role members: a person adds IsaacF to 'Region Manager' and ColinB to 'Business User' in the
Power BI service.
Manual demo steps (Prep data for AI, seeding, rehearsal) are in README.md.
Usage:  pwsh -File scripts\\Deploy-CaldovaFinance.ps1 -Step workspaces,load,model,refresh,connection,permissions,validate
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import pathlib
import shutil
import sys
import tempfile
import time

import caldova_fabric as cf
import fabric_helpers as fh

ROOT = cf.ROOT
CFG = cf.CFG
FAB = CFG["fabric"]
USERS = {role: cf.upn(alias) for role, alias in CFG["users"].items()}
CAPACITY_ID = CFG.get("fabricCapacity", {}).get("capacityId") or None
if CAPACITY_ID and "<" in CAPACITY_ID:
    CAPACITY_ID = None
DATA = ROOT / "data" / "finance"
FABRIC_DIR = ROOT / "fabric"
MODEL = FAB["semanticModel"]
REPORTS = {"overview": FAB["report"]}
BUSINESS_USERS = {  # persona -> RLS role; neither gets a role on the data workspace, so RLS applies to both
    "regionManager": FAB.get("rlsRoleRegion", "Region Manager"),
    "businessUser": FAB["rlsRole"],
}
STATE_FILE = ROOT / ".deploy-state" / "finance.json"
STEPS = ["workspaces", "load", "model", "refresh", "connection", "permissions", "reports", "validate"]


def log(msg: str) -> None:
    print(f"[finance] {msg}", flush=True)


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def find_one(items: list[dict], name: str, what: str) -> dict:
    match = [i for i in items if i["displayName"] == name]
    if len(match) != 1:
        raise RuntimeError(f"Expected exactly one {what} named '{name}', found {len(match)}")
    return match[0]


# ---------------------------------------------------------------- workspaces + lakehouse
def step_workspaces(state: dict) -> None:
    data_ws = fh.ensure_workspace(FAB["dataWorkspace"], "Caldova finance data: lakehouse and the Supplier Invoice "
                                  "Assurance semantic model (synthetic demo data).", CAPACITY_ID)
    insights_ws = fh.ensure_workspace(FAB["insightsWorkspace"], "Caldova finance insights for business users: the "
                                      "Supplier Invoice Assurance report.", CAPACITY_ID)
    lakehouse = fh.ensure_lakehouse(data_ws, FAB["lakehouse"],
                                    "Caldova supplier invoices checked against contract prices (synthetic demo data).")
    log(f"'{FAB['dataWorkspace']}' {data_ws}, '{FAB['insightsWorkspace']}' {insights_ws}, {FAB['lakehouse']} {lakehouse}")
    for ws in (data_ws, insights_ws):
        fh.ensure_role(ws, USERS["dataAnalyst"], "Admin")
    fh.ensure_role(insights_ws, USERS["regionManager"], "Contributor")
    fh.ensure_role(insights_ws, USERS["businessUser"], "Viewer")
    data_roles = {a["principal"]["id"] for a in cf.fabric_list(f"/workspaces/{data_ws}/roleAssignments")}
    for persona in BUSINESS_USERS:
        if cf.graph_user_id(USERS[persona]) in data_roles:
            raise RuntimeError(f"{USERS[persona]} has a role on '{FAB['dataWorkspace']}': remove it. Business users "
                               "must only use the Insights workspace (a workspace role there bypasses RLS)")
    state.update(dataWorkspaceId=data_ws, insightsWorkspaceId=insights_ws, lakehouseId=lakehouse)


def step_load(state: dict, data_dir: pathlib.Path = DATA, only: set[str] | None = None) -> None:
    import pyarrow as pa
    import pyarrow.csv as pacsv
    from deltalake import write_deltalake

    arrow = {"int64": pa.int64(), "double": pa.float64(), "string": pa.string(), "date": pa.date32(),
             "boolean": pa.bool_(), "decimal2": pa.decimal128(18, 2), "decimal4": pa.decimal128(18, 4)}
    schema = json.loads((data_dir / "_schema.json").read_text(encoding="utf-8"))
    base = f"abfss://{state['dataWorkspaceId']}@onelake.dfs.fabric.microsoft.com/{state['lakehouseId']}/Tables/dbo"
    for table, cols in schema.items():
        if only and table not in only:
            continue
        if not table.startswith("fin_"):
            raise RuntimeError(f"Refusing to write {table}: finance tables must be prefixed fin_")
        pa_schema = pa.schema([(c, arrow[t]) for c, t in cols])
        text = cf.resolve_tenant((data_dir / f"{table}.csv").read_text(encoding="utf-8"))
        data = pacsv.read_csv(io.BytesIO(text.encode("utf-8")), convert_options=pacsv.ConvertOptions(
            column_types=pa_schema, strings_can_be_null=True, include_columns=[c for c, _ in cols]))
        data = data.select([c for c, _ in cols]).cast(pa_schema)
        write_deltalake(f"{base}/{table}", data, mode="overwrite", schema_mode="overwrite",
                        storage_options=cf.onelake_storage_options())
        log(f"  dbo.{table:30s} {data.num_rows:>6,} rows")
    state["dataLoadedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------- semantic model
def step_model(state: dict, update: bool) -> None:
    ws = state["dataWorkspaceId"]
    folder = FABRIC_DIR / f"{MODEL}.SemanticModel"
    platform = json.loads((folder / ".platform").read_text(encoding="utf-8"))
    parts = fh.model_parts(folder, state)
    existing = [m for m in cf.fabric_list(f"/workspaces/{ws}/semanticModels") if m["displayName"] == MODEL]
    if len(existing) > 1:
        raise RuntimeError(f"More than one model named '{MODEL}' - delete the duplicates first")
    if existing:
        mid = existing[0]["id"]
        if not update:
            log(f"model '{MODEL}' exists ({mid}) - left untouched (use --update-model to push TMDL changes)")
        else:
            remote = cf.fabric("POST", f"/workspaces/{ws}/semanticModels/{mid}/getDefinition?format=TMDL")
            extra = sorted({p["path"] for p in remote["definition"]["parts"]} - {p["path"] for p in parts} - {".platform"})
            # Tables and roles are defined by the repo's model.tmdl, so a table/role file missing from the repo is an
            # intentional removal. Anything else (e.g. Prep data for AI, linguistic metadata) is service-side content.
            removed = [p for p in extra if p.startswith(("definition/tables/", "definition/roles/"))]
            extra = [p for p in extra if p not in removed]
            if extra:
                raise RuntimeError(f"'{MODEL}' has service-side parts not in the repo {extra} (e.g. Prep data for AI). "
                                   "Update aborted to preserve them - export the model to the repo first")
            if removed:
                log(f"  removing tables/roles no longer in the repo: {removed}")
            cf.fabric("POST", f"/workspaces/{ws}/semanticModels/{mid}/updateDefinition",
                      {"definition": {"format": "TMDL", "parts": parts}})
            log(f"model '{MODEL}' definition updated ({mid})")
    else:
        cf.fabric("POST", f"/workspaces/{ws}/semanticModels", {
            "displayName": MODEL, "description": platform["metadata"].get("description", ""),
            "definition": {"format": "TMDL", "parts": parts}}, retry=False)
        mid = find_one(cf.fabric_list(f"/workspaces/{ws}/semanticModels"), MODEL, "semantic model")["id"]
        log(f"model '{MODEL}' created ({mid})")
    state["semanticModelId"] = mid


def step_refresh(state: dict) -> None:
    ws, mid = state["dataWorkspaceId"], state["semanticModelId"]
    # New Delta tables must be in the lakehouse catalog before Direct Lake can frame them: sync it first
    sql_id = cf.fabric("GET", f"/workspaces/{ws}/lakehouses/{state['lakehouseId']}")["properties"][
        "sqlEndpointProperties"]["id"]
    cf.fabric("POST", f"/workspaces/{ws}/sqlEndpoints/{sql_id}/refreshMetadata", {}, retry=False)
    cf.pbi("POST", f"/groups/{ws}/datasets/{mid}/refreshes", {"notifyOption": "NoNotification"})
    for _ in range(60):
        time.sleep(5)
        last = cf.pbi("GET", f"/groups/{ws}/datasets/{mid}/refreshes?$top=1").json()["value"][0]
        if last["status"] in ("Completed", "Failed", "Disabled", "Cancelled"):
            break
    if last["status"] != "Completed":
        raise RuntimeError(f"Refresh ended {last['status']}: {json.dumps(last)[:1500]}")
    log(f"model '{MODEL}' reframed (Direct Lake) - {last['status']}")


# ---------------------------------------------------------------- fixed identity for Direct Lake
def create_onelake_connection(path: str, name: str) -> dict:
    """ShareableCloud OneLake (ADLS) connection with workspace-identity credentials whose path equals `path`."""
    server = path[: path.index("/", len("https://"))]
    sub = path[len(server):]
    errors = []
    for path_value in (sub, sub.rstrip("/")):
        body = {
            "connectivityType": "ShareableCloud", "displayName": name,
            "connectionDetails": {"type": "AzureDataLakeStorage", "creationMethod": "AzureDataLakeStorage",
                                  "parameters": [{"dataType": "Text", "name": "server", "value": server},
                                                 {"dataType": "Text", "name": "path", "value": path_value}]},
            "privacyLevel": "Organizational", "allowConnectionUsageInGateway": False,
            "credentialDetails": {"singleSignOnType": "None", "connectionEncryption": "NotEncrypted",
                                  "skipTestConnection": False, "credentials": {"credentialType": "WorkspaceIdentity"}},
        }
        try:
            conn = cf.fabric("POST", "/connections", body, retry=False)
        except RuntimeError as exc:
            errors.append(str(exc)[:400])
            continue
        if conn["connectionDetails"]["path"] == path:
            return conn
        errors.append(f"path {conn['connectionDetails']['path']!r} != {path!r}")
        cf.fabric("DELETE", f"/connections/{conn['id']}")
    raise RuntimeError(f"Could not create a OneLake connection matching {path}: {errors}")


def step_connection(state: dict) -> None:
    ws, mid, name = state["dataWorkspaceId"], state["semanticModelId"], FAB["connectionName"]
    identity = cf.fabric("GET", f"/workspaces/{ws}").get("workspaceIdentity")
    if not identity:
        cf.fabric("POST", f"/workspaces/{ws}/provisionIdentity")
        for _ in range(12):
            identity = cf.fabric("GET", f"/workspaces/{ws}").get("workspaceIdentity")
            if identity:
                break
            time.sleep(5)
        if not identity:
            raise RuntimeError("Workspace identity was not provisioned")
        log(f"workspace identity created for '{FAB['dataWorkspace']}' (application {identity['applicationId']})")
    else:
        log(f"workspace identity exists (application {identity['applicationId']})")
    sp = identity["servicePrincipalId"]
    if not any(a["principal"]["id"] == sp for a in cf.fabric_list(f"/workspaces/{ws}/roleAssignments")):
        cf.fabric("POST", f"/workspaces/{ws}/roleAssignments",
                  {"principal": {"id": sp, "type": "ServicePrincipal"}, "role": "Contributor"})
        log("  workspace identity: Contributor on the workspace (OneLake read for Direct Lake)")
    lake = [c for c in cf.fabric_list(f"/workspaces/{ws}/items/{mid}/connections")
            if c["connectionDetails"]["type"] == "AzureDataLakeStorage"]
    if len(lake) != 1:
        raise RuntimeError(f"Expected one OneLake data source on '{MODEL}', found {len(lake)}")
    ref = lake[0]
    conn = next((c for c in cf.fabric_list("/connections") if c["displayName"] == name), None)
    if conn:
        log(f"connection '{name}' exists ({conn['id']})")
    else:
        conn = create_onelake_connection(ref["connectionDetails"]["path"], name)
        log(f"connection '{name}' created ({conn['id']}): workspace identity, SSO off")
    owner = cf.graph_user_id(USERS["dataAnalyst"])
    if not any(a["principal"]["id"] == owner for a in cf.fabric_list(f"/connections/{conn['id']}/roleAssignments")):
        cf.fabric("POST", f"/connections/{conn['id']}/roleAssignments",
                  {"principal": {"id": owner, "type": "User"}, "role": "Owner"})
        log(f"  {USERS['dataAnalyst']}: Owner of the connection")
    if ref.get("id") == conn["id"]:
        log(f"  '{MODEL}' already bound to the fixed identity")
    else:
        cf.fabric("POST", f"/workspaces/{ws}/semanticModels/{mid}/bindConnection",
                  {"connectionBinding": {"id": conn["id"], "connectivityType": "ShareableCloud",
                                         "connectionDetails": ref["connectionDetails"]}})
        if not any(c.get("id") == conn["id"] for c in cf.fabric_list(f"/workspaces/{ws}/items/{mid}/connections")):
            raise RuntimeError("The binding is not visible after bindConnection")
        log(f"  '{MODEL}' bound to the fixed identity (SSO off)")
    state["connectionId"] = conn["id"]


def step_permissions(state: dict) -> None:
    ws, mid = state["dataWorkspaceId"], state["semanticModelId"]
    users = cf.pbi("GET", f"/groups/{ws}/datasets/{mid}/users").json().get("value", [])
    for persona, rls_role in BUSINESS_USERS.items():
        upn = USERS[persona]
        body = {"identifier": upn, "principalType": "User", "datasetUserAccessRight": "ReadExplore"}
        if any(u.get("identifier", "").lower() == upn.lower() for u in users):
            cf.pbi("PUT", f"/groups/{ws}/datasets/{mid}/users", body)
        else:
            cf.pbi("POST", f"/groups/{ws}/datasets/{mid}/users", body)
        log(f"{upn}: Read + Build (ReadExplore) on '{MODEL}' (no workspace role in '{FAB['dataWorkspace']}')")
        log(f"RLS: add {upn} to the '{rls_role}' role of '{MODEL}' in the Power BI service (never scripted)")


# ---------------------------------------------------------------- reports (powerbi-report-cli management mode)
def step_reports(state: dict, update: bool = False) -> None:
    data_ws, insights_ws, mid = state["dataWorkspaceId"], state["insightsWorkspaceId"], state["semanticModelId"]
    names = fh.deployed_model_names(data_ws, mid)
    published = state.setdefault("reports", {})
    for key, name in REPORTS.items():
        folder = FABRIC_DIR / f"{name}.Report"
        if not folder.exists():
            log(f"report '{name}': no local PBIR ({folder.relative_to(ROOT)}) - skipped")
            continue
        missing = fh.missing_bindings(folder, names)
        if missing:
            raise RuntimeError(f"'{name}' binds fields missing from deployed '{MODEL}': {missing}")
        existing = [r for r in cf.fabric_list(f"/workspaces/{insights_ws}/reports", skill=cf.SKILL_REPORT)
                    if r["displayName"] == name]
        if len(existing) > 1:
            raise RuntimeError(f"More than one report named '{name}' in '{FAB['insightsWorkspace']}' - resolve manually")
        if existing and not update:
            published[key] = existing[0]["id"]
            log(f"report '{name}' exists ({existing[0]['id']}) - left untouched (use --update-reports to overwrite)")
            continue
        staging = pathlib.Path(tempfile.mkdtemp(prefix="caldova-fin-report-"))
        try:
            staged = fh.stage_report(folder, mid, staging)
            check = fh.pbir_cli("validate", str(staged))["data"]
            if check.get("errorCount"):
                raise RuntimeError(f"PBIR validation failed for staged '{name}': {json.dumps(check)[:1500]}")
            body_file = staging / "body.json"
            if existing:
                rid = existing[0]["id"]
                fh.pbir_cli("pack", str(staged), "--raw", "--out", str(body_file))
                cf.fabric("POST", f"/workspaces/{insights_ws}/reports/{rid}/updateDefinition",
                          json.loads(body_file.read_text(encoding="utf-8")), skill=cf.SKILL_REPORT)
                log(f"report '{name}' definition overwritten ({rid})")
            else:
                fh.pbir_cli("pack", str(staged), "--raw", "--mode", "create", "--display-name", name,
                            "--description", f"Caldova finance - live on {MODEL} ({FAB['dataWorkspace']})",
                            "--out", str(body_file))
                cf.fabric("POST", f"/workspaces/{insights_ws}/reports",
                          json.loads(body_file.read_text(encoding="utf-8")), skill=cf.SKILL_REPORT, retry=False)
                rid = find_one(cf.fabric_list(f"/workspaces/{insights_ws}/reports", skill=cf.SKILL_REPORT), name,
                               "report")["id"]
                log(f"report '{name}' created ({rid})")
            sent = len(json.loads(body_file.read_text(encoding="utf-8"))["definition"]["parts"])
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        info = cf.pbi("GET", f"/groups/{insights_ws}/reports/{rid}").json()
        if info.get("datasetId", "").lower() != mid.lower():
            raise RuntimeError(f"'{name}' is bound to dataset {info.get('datasetId')}, expected {mid}")
        remote = cf.fabric("POST", f"/workspaces/{insights_ws}/reports/{rid}/getDefinition?format=PBIR",
                           skill=cf.SKILL_REPORT)["definition"]
        pbir = next(p for p in remote["parts"] if p["path"] == "definition.pbir")
        if f"semanticmodelid={mid}".lower() not in base64.b64decode(pbir["payload"]).decode("utf-8").lower():
            raise RuntimeError(f"'{name}' readback definition.pbir does not reference {mid}")
        log(f"  readback OK: {len(remote['parts'])} parts (sent {sent}), bound to {MODEL}; {info.get('webUrl')}")
        published[key] = rid


# ---------------------------------------------------------------- validation
def num(v) -> float:
    return round(float(v or 0), 2)


def step_validate(state: dict, data_dir: pathlib.Path = DATA) -> None:
    ws, mid = state["dataWorkspaceId"], state["semanticModelId"]
    exp = json.loads(cf.resolve_tenant((data_dir / "expected_answers.json").read_text(encoding="utf-8")))
    dax, check = fh.dax, fh.check
    failures: list[str] = []
    lo, hi = ([int(p) for p in d.split("-")] for d in exp["windows"]["last_4_weeks"])
    last_q = (f"DATESBETWEEN ( 'Date'[Date], DATE ( {lo[0]}, {lo[1]}, {lo[2]} ), "
              f"DATE ( {hi[0]}, {hi[1]}, {hi[2]} ) )")

    def by(column: str, label: str, impersonate: str | None) -> dict:
        rows = dax(ws, mid, f"EVALUATE SUMMARIZECOLUMNS ( {column}, {last_q}, \"o\", [Overbilled Amount] ) "
                            f"ORDER BY {column}", impersonate)
        return {x[label]: num(x["o"]) for x in rows if x["o"]}

    def persona(name: str, e: dict, countries: int, impersonate: str | None = None) -> None:
        log(f"{name}: last 4 weeks = {exp['last_4_weeks']}")
        r = dax(ws, mid, "EVALUATE CALCULATETABLE ( ROW ( \"C\", COUNTROWS ( Countries ), \"I\", [Invoices], "
                         "\"E\", [Invoices with Errors], \"Acc\", [Invoice Accuracy %], "
                         "\"Prev\", [Invoice Accuracy % Previous 4 Weeks], \"Inv\", [Invoiced Amount], "
                         f"\"Over\", [Overbilled Amount], \"Sup\", [Suppliers with Overbilling] ), {last_q} )",
                impersonate)[0]
        lq, pq = e["last_4_weeks"], e["previous_4_weeks"]
        check(f"{name}: countries visible", r["C"], countries, failures)
        check(f"{name}: invoices / with errors", (r["I"], r["E"] or 0), (lq["invoices"], lq["invoices_with_errors"]),
              failures)
        check(f"{name}: invoice accuracy previous -> last 4 weeks (%)",
              (round(r["Prev"] * 100, 1), round(r["Acc"] * 100, 1)),
              (pq["invoice_accuracy_pct"], lq["invoice_accuracy_pct"]), failures)
        check(f"{name}: invoiced / overbilled", (num(r["Inv"]), num(r["Over"])),
              (lq["invoiced_usd"], lq["overbilled_usd"]), failures)
        check(f"{name}: suppliers with overbilling", r["Sup"] or 0, lq["suppliers_with_overbilling"], failures)
        check(f"{name}: overbilled by country", by("Countries[Country]", "Country", impersonate),
              e["last_4_weeks_overbilled_by_country"], failures)
        check(f"{name}: overbilled by supplier", by("Suppliers[Supplier Name]", "Supplier Name", impersonate),
              e["last_4_weeks_overbilled_by_supplier"], failures)
        check(f"{name}: overbilled by error type", by("'Error Types'[Error Type]", "Error Type", impersonate),
              {k: v["overbilled_usd"] for k, v in lq["by_error_type"].items() if v["overbilled_usd"]}, failures)
        b = dax(ws, mid, f"EVALUATE CALCULATETABLE ( ROW ( \"P\", [Payments to Block], \"N\", [Invoices to Block] ), "
                         f"{last_q} )", impersonate)[0]
        check(f"{name}: payments to block / invoices", (num(b["P"]), b["N"] or 0),
              (lq["payments_to_block_usd"], lq["invoices_to_block"]), failures)
        c = dax(ws, mid, "EVALUATE ROW ( \"N\", COUNTROWS ( Contracts ), \"Code\", "
                         "CALCULATE ( SELECTEDVALUE ( Contracts[Contract Unit Price] ), "
                         f"Contracts[Contract Code] = \"{ann['contract_code']}\" ) )", impersonate)[0]
        check(f"{name}: contracts visible / {ann['contract_code']} price in the contract database",
              (c["N"], num(c["Code"])), (10 * countries, ann["price_in_contract_database"]), failures)

    ann = exp["annterra_germany_amendment"]
    persona("Deployer / workspace Admin (all rows)", exp["personas"][USERS["regionManager"]], 6)
    for key, countries, name in (("regionManager", 6, "Isaac"), ("businessUser", 1, "Colin")):
        upn, rls_role = USERS[key], BUSINESS_USERS[key]
        try:
            persona(f"{name} via RLS impersonation ({rls_role})", exp["personas"][upn], countries, upn)
        except RuntimeError as exc:
            failures.append(f"{name} RLS")
            print(f"  FAIL {name} RLS: {str(exc)[:300]} -> add {upn} to the '{rls_role}' role in the Power BI service")
    if failures:
        raise SystemExit(f"{len(failures)} validation check(s) failed: {failures}")
    log("all validation checks passed")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 epilog=f"Steps (in order): {', '.join(STEPS)}")
    ap.add_argument("--steps", default="all", help="'all' or a comma-separated list of steps")
    ap.add_argument("--update-model", action="store_true", help="push local TMDL changes to an existing model")
    ap.add_argument("--update-reports", action="store_true", help="overwrite an already-published report")
    args = ap.parse_args()
    steps = STEPS if args.steps == "all" else [s.strip() for s in args.steps.split(",") if s.strip()]
    unknown = set(steps) - set(STEPS)
    if unknown:
        raise SystemExit(f"Unknown step(s): {sorted(unknown)}; valid: {STEPS}")
    cf.guard_profile()
    log(f"signed in as {cf.signed_in_user()} (tenant {CFG['tenantDomain']})")
    state = load_state()
    if steps[0] != "workspaces" and "dataWorkspaceId" not in state:
        steps = ["workspaces", *steps]
    for step in steps:
        log(f"=== {step}")
        if step == "model":
            step_model(state, args.update_model)
        elif step == "reports":
            step_reports(state, args.update_reports)
        else:
            globals()[f"step_{step}"](state)
        save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
