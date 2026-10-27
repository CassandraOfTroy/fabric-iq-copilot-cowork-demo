"""Fabric, Power BI, Graph and OneLake helpers pinned to the demo tenant in config/tenant.json.

Tokens come from the Azure CLI profile in AZURE_CONFIG_DIR (the repo-local folder named by azureConfigDir in
config/tenant.json), never from your default/corporate Azure CLI profile (%USERPROFILE%\\.azure). Every token is
checked for the configured tenant ID (tid claim) before it is used. Every api.fabric.microsoft.com call - including long-running-operation polls - carries
the x-ms-fabric-skill telemetry header.

Grounding:
  https://learn.microsoft.com/cli/azure/use-azure-cli-successfully-tips  (AZURE_CONFIG_DIR isolation)
  https://learn.microsoft.com/rest/api/fabric/articles/long-running-operation
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import shutil
import subprocess
import time
from typing import Any

import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "config" / "tenant.json"
TENANT_TOKEN = "{{TENANT_DOMAIN}}"  # placeholder for the tenant domain in data/finance (UPNs)


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise SystemExit(
            f"{CONFIG_FILE} not found. Copy config/tenant.example.json to config/tenant.json and fill in your tenant "
            "(tenantId, tenantDomain, Fabric capacity). config/tenant.json is git-ignored.")
    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    unset = [k for k in ("tenantId", "tenantDomain")
             if not cfg.get(k) or "<" in cfg[k] or cfg[k].startswith("00000000-")]
    if unset:
        raise SystemExit(f"config/tenant.json still has placeholder values for {unset}: fill in your tenant")
    return cfg


CFG = load_config()


def upn(alias: str) -> str:
    """Demo users are configured as aliases; the UPN is <alias>@<tenantDomain>."""
    return alias if "@" in alias else f"{alias}@{CFG['tenantDomain']}"


def resolve_tenant(text: str) -> str:
    """Replace the {{TENANT_DOMAIN}} placeholder used in data/finance with the configured tenant domain."""
    return text.replace(TENANT_TOKEN, CFG["tenantDomain"])


FABRIC = "https://api.fabric.microsoft.com/v1"
PBI = "https://api.powerbi.com/v1.0/myorg"
GRAPH = "https://graph.microsoft.com/v1.0"
RES_FABRIC = "https://api.fabric.microsoft.com"
RES_PBI = "https://analysis.windows.net/powerbi/api"
RES_STORAGE = "https://storage.azure.com"
RES_GRAPH = "https://graph.microsoft.com"

SKILL_MODEL = "semantic-model-authoring"
SKILL_REPORT = "powerbi-report-cli"


class TenantGuardError(RuntimeError):
    pass


def guard_profile() -> None:
    """Refuse to run unless the Azure CLI is pointed at the repo-local demo-tenant profile."""
    expected = (ROOT / CFG["azureConfigDir"]).resolve()
    actual = os.environ.get("AZURE_CONFIG_DIR")
    if not actual or pathlib.Path(actual).resolve() != expected:
        raise TenantGuardError(
            f"AZURE_CONFIG_DIR is '{actual}', expected '{expected}'. "
            "Run through scripts\\Deploy-CaldovaFinance.ps1 (or dot-source scripts\\Use-CaldovaTenant.ps1 first) - "
            "never against your default/corporate Azure CLI profile."
        )


def _claims(tok: str) -> dict[str, Any]:
    payload = tok.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


_TOKENS: dict[str, tuple[str, float]] = {}


def token(resource: str) -> str:
    cached = _TOKENS.get(resource)
    if cached and cached[1] - 300 > time.time():
        return cached[0]
    guard_profile()
    az = shutil.which("az") or shutil.which("az.cmd")
    if not az:
        raise RuntimeError("Azure CLI (az) not found on PATH")
    out = subprocess.run(
        [az, "account", "get-access-token", "--resource", resource, "--tenant", CFG["tenantId"], "--output", "json"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"az get-access-token failed for {resource}: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    tok = data["accessToken"]
    tid = _claims(tok).get("tid")
    if tid != CFG["tenantId"]:
        raise TenantGuardError(f"Token for {resource} issued by tenant {tid}, not the configured tenant {CFG['tenantId']}")
    expires = float(data.get("expires_on") or time.time() + 1800)
    _TOKENS[resource] = (tok, expires)
    return tok


def signed_in_user() -> str:
    c = _claims(token(RES_FABRIC))
    return c.get("upn") or c.get("unique_name") or c.get("oid")


def _request(method: str, url: str, resource: str, body: Any = None, skill: str = SKILL_MODEL,
             ok: tuple[int, ...] = (200, 201, 202, 204), retries: int = 6) -> requests.Response:
    headers = {"Authorization": f"Bearer {token(resource)}"}
    if url.startswith(RES_FABRIC):
        headers["x-ms-fabric-skill"] = skill
    if body is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries):
        r = requests.request(method, url, headers=headers, json=body, timeout=180)
        if r.status_code == 429 or (r.status_code >= 500 and attempt < retries - 1):
            time.sleep(int(r.headers.get("Retry-After", 10 * (attempt + 1))))
            continue
        break
    if r.status_code not in ok:
        raise RuntimeError(f"{method} {url} -> HTTP {r.status_code}: {r.text[:1500]}")
    return r


def _wait_operation(r: requests.Response, skill: str) -> Any:
    location = r.headers.get("Location")
    op_id = r.headers.get("x-ms-operation-id")
    status_url = location if location and "/operations/" in location else f"{FABRIC}/operations/{op_id}"
    while True:
        time.sleep(int(r.headers.get("Retry-After", 5)))
        s = _request("GET", status_url, RES_FABRIC, skill=skill)
        body = s.json() if s.content else {}
        status = body.get("status")
        if status == "Succeeded":
            res = requests.get(status_url.rstrip("/") + "/result", timeout=120, headers={
                "Authorization": f"Bearer {token(RES_FABRIC)}", "x-ms-fabric-skill": skill})
            return res.json() if res.status_code == 200 and res.content else body
        if status in ("Failed", "Cancelled", "Undefined"):
            raise RuntimeError(f"Fabric operation {status}: {json.dumps(body)[:2000]}")
        r = s


def fabric(method: str, path: str, body: Any = None, skill: str = SKILL_MODEL, retry: bool = True) -> Any:
    # retry=False for create POSTs: a retried create can produce a duplicate item
    r = _request(method, FABRIC + path, RES_FABRIC, body, skill, retries=6 if retry else 1)
    if r.status_code == 202:
        return _wait_operation(r, skill)
    return r.json() if r.content else None


def fabric_list(path: str, skill: str = SKILL_MODEL) -> list[dict]:
    items, url = [], FABRIC + path
    while url:
        body = _request("GET", url, RES_FABRIC, skill=skill).json()
        items.extend(body.get("value", []))
        url = body.get("continuationUri")
    return items


def pbi(method: str, path: str, body: Any = None, ok: tuple[int, ...] = (200, 201, 202, 204)) -> requests.Response:
    return _request(method, PBI + path, RES_PBI, body, ok=ok)


def graph_user_id(upn: str) -> str:
    return _request("GET", f"{GRAPH}/users/{upn}?$select=id,userPrincipalName", RES_GRAPH).json()["id"]


def onelake_storage_options() -> dict[str, str]:
    return {"bearer_token": token(RES_STORAGE), "use_fabric_endpoint": "true"}


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
