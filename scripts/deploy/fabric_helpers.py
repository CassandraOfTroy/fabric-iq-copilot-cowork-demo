"""Generic Fabric / Power BI helpers used by deploy_finance.py: workspace roles, TMDL parts, PBIR staging and
binding checks, the powerbi-report-author CLI wrapper, and DAX execution for validation.
"""
from __future__ import annotations

import base64
import json
import pathlib
import re
import shutil
import subprocess

import caldova_fabric as cf

ROOT = cf.ROOT
PBIR_CLI = ROOT / "scripts" / "reports" / "Invoke-PbirCli.ps1"


def log(msg: str) -> None:
    print(f"[deploy] {msg}", flush=True)


# ---------------------------------------------------------------- workspaces
def ensure_workspace(name: str, description: str, capacity_id: str | None) -> str:
    """Resolve the workspace by name, creating it on the configured capacity if it doesn't exist."""
    match = [w for w in cf.fabric_list("/workspaces") if w["displayName"] == name]
    if len(match) > 1:
        raise RuntimeError(f"More than one workspace named '{name}' - resolve manually first")
    if match:
        ws = match[0]
        log(f"workspace '{name}' exists ({ws['id']})")
    else:
        if not capacity_id:
            raise RuntimeError(f"Workspace '{name}' does not exist and fabricCapacity.capacityId is not set in "
                               "config/tenant.json: create the workspace or set the capacity ID")
        ws = cf.fabric("POST", "/workspaces", {"displayName": name, "description": description,
                                               "capacityId": capacity_id}, retry=False)
        log(f"workspace '{name}' created ({ws['id']})")
    if capacity_id:
        detail = cf.fabric("GET", f"/workspaces/{ws['id']}")
        if detail.get("capacityId", "").lower() != capacity_id.lower():
            cf.fabric("POST", f"/workspaces/{ws['id']}/assignToCapacity", {"capacityId": capacity_id})
            log(f"  assigned to capacity {capacity_id}")
    return ws["id"]


def ensure_lakehouse(ws: str, name: str, description: str) -> str:
    match = [i for i in cf.fabric_list(f"/workspaces/{ws}/lakehouses") if i["displayName"] == name]
    if len(match) > 1:
        raise RuntimeError(f"More than one lakehouse named '{name}' - resolve manually first")
    if match:
        log(f"lakehouse '{name}' exists ({match[0]['id']})")
        return match[0]["id"]
    lh = cf.fabric("POST", f"/workspaces/{ws}/lakehouses", {
        "displayName": name, "description": description, "creationPayload": {"enableSchemas": True}}, retry=False)
    if not lh or "id" not in lh:
        lh = [i for i in cf.fabric_list(f"/workspaces/{ws}/lakehouses") if i["displayName"] == name][0]
    log(f"lakehouse '{name}' created ({lh['id']})")
    return lh["id"]


def ensure_role(ws_id: str, upn: str, role: str) -> None:
    oid = cf.graph_user_id(upn)
    existing = {a["principal"]["id"]: a for a in cf.fabric_list(f"/workspaces/{ws_id}/roleAssignments")}
    if oid in existing:
        current = existing[oid]["role"]
        if current != role:
            cf.fabric("PATCH", f"/workspaces/{ws_id}/roleAssignments/{existing[oid]['id']}", {"role": role})
            log(f"  {upn}: {current} -> {role}")
        else:
            log(f"  {upn}: {role} (unchanged)")
        return
    cf.fabric("POST", f"/workspaces/{ws_id}/roleAssignments", {"principal": {"id": oid, "type": "User"}, "role": role})
    log(f"  {upn}: {role} (added)")


# ---------------------------------------------------------------- semantic model
def model_parts(folder: pathlib.Path, state: dict) -> list[dict]:
    parts = []
    for f in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = f.relative_to(folder).as_posix()
        if rel == ".platform" or rel.startswith("."):
            continue
        content = f.read_bytes()
        if rel.endswith(".tmdl"):
            text = content.decode("utf-8").replace("{{WORKSPACE_ID}}", state["dataWorkspaceId"]) \
                                          .replace("{{LAKEHOUSE_ID}}", state["lakehouseId"])
            text = cf.resolve_tenant(text)
            if "{{" in text:
                raise RuntimeError(f"Unresolved placeholder in {rel}")
            content = text.encode("utf-8")
        parts.append({"path": rel, "payload": cf.b64(content), "payloadType": "InlineBase64"})
    return parts


# ---------------------------------------------------------------- reports (powerbi-report-cli management mode)
def pbir_cli(*args: str) -> dict:
    """Run powerbi-report-author through the repo wrapper (portable Node 24; see Invoke-PbirCli.ps1)."""
    proc = subprocess.run(["pwsh", "-NoProfile", "-File", str(PBIR_CLI), *args],
                          capture_output=True, text=True, encoding="utf-8")
    out = proc.stdout.strip()
    start = out.find("{")
    try:
        result = json.loads(out[start:]) if start >= 0 else {}
    except json.JSONDecodeError:
        result = {}
    if proc.returncode != 0 or "error" in result:
        raise RuntimeError(f"powerbi-report-author {args[0]} failed: {out[-1500:]} {proc.stderr[-800:]}")
    return result


def deployed_model_names(ws: str, mid: str) -> dict[str, dict[str, set[str]]]:
    """Tables -> {'column': names, 'measure': names} parsed from the deployed model's TMDL definition."""
    definition = cf.fabric("POST", f"/workspaces/{ws}/semanticModels/{mid}/getDefinition?format=TMDL",
                           skill=cf.SKILL_REPORT)
    names: dict[str, dict[str, set[str]]] = {}
    unq = lambda s: s.strip().strip("'")  # noqa: E731
    for part in definition["definition"]["parts"]:
        if not part["path"].startswith("definition/tables/"):
            continue
        body = base64.b64decode(part["payload"]).decode("utf-8")
        table = unq(re.search(r"^table (.+)$", body, re.M).group(1))
        names[table] = {"column": {unq(c) for c in re.findall(r"^\tcolumn ('[^']+'|[^\s=]+)", body, re.M)},
                        "measure": {unq(m) for m in re.findall(r"^\tmeasure ('[^']+'|[^\s=]+)", body, re.M)}}
    return names


def report_bindings(node, aliases: dict[str, str] | None = None, found: set | None = None) -> set[tuple[str, str, str]]:
    """Every (kind, table, name) referenced by Column/Measure expressions, resolving filter From aliases."""
    found = set() if found is None else found
    aliases = dict(aliases or {})
    if isinstance(node, dict):
        if isinstance(node.get("From"), list):
            aliases.update({f["Name"]: f["Entity"] for f in node["From"] if "Name" in f and "Entity" in f})
        for kind in ("Column", "Measure"):
            expr = node.get(kind)
            if isinstance(expr, dict) and "Property" in expr:
                ref = expr.get("Expression", {}).get("SourceRef", {})
                table = ref.get("Entity") or aliases.get(ref.get("Source", ""))
                if table:
                    found.add((kind.lower(), table, expr["Property"]))
        for value in node.values():
            report_bindings(value, aliases, found)
    elif isinstance(node, list):
        for value in node:
            report_bindings(value, aliases, found)
    return found


def missing_bindings(folder: pathlib.Path, names: dict[str, dict[str, set[str]]]) -> list[str]:
    refs: set[tuple[str, str, str]] = set()
    for f in (folder / "definition").rglob("*.json"):
        report_bindings(json.loads(f.read_text(encoding="utf-8")), found=refs)
    return sorted(f"{t}[{n}] ({k})" for k, t, n in refs if n not in names.get(t, {}).get(k, set()))


def stage_report(folder: pathlib.Path, model_id: str, staging: pathlib.Path) -> pathlib.Path:
    """Disposable copy for publishing: PBIR parts only (never .pbi caches), definition.pbir rebound to the API form."""
    dest = staging / folder.name
    dest.mkdir(parents=True)
    for sub in ("definition", "StaticResources"):
        if (folder / sub).exists():
            shutil.copytree(folder / sub, dest / sub)
    shutil.copy2(folder / ".platform", dest / ".platform")
    pbir = json.loads((folder / "definition.pbir").read_text(encoding="utf-8"))
    # Fabric REST publish form (byConnection); the local PBIP keeps byPath for Power BI Desktop and Git
    pbir["datasetReference"] = {"byConnection": {"connectionString": f"semanticmodelid={model_id}"}}
    (dest / "definition.pbir").write_text(json.dumps(pbir, indent=2), encoding="utf-8")
    return dest


# ---------------------------------------------------------------- validation
def dax(ws: str, mid: str, query: str, impersonate: str | None = None) -> list[dict]:
    body: dict = {"queries": [{"query": query}], "serializerSettings": {"includeNulls": True}}
    if impersonate:
        body["impersonatedUserName"] = impersonate
    res = cf.pbi("POST", f"/groups/{ws}/datasets/{mid}/executeQueries", body).json()
    table = res["results"][0]["tables"][0]
    return [{k.split("[")[-1].rstrip("]"): v for k, v in row.items()} for row in table.get("rows", [])]


def check(label: str, actual, expected, failures: list[str]) -> None:
    ok = actual == expected
    print(f"  {'PASS' if ok else 'FAIL'} {label}: {actual!r}" + ("" if ok else f" (expected {expected!r})"))
    if not ok:
        failures.append(label)
