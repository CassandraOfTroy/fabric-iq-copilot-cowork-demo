"""Optional, after the demo: Laurence's fix at the source (update a contract price and refresh the model).

Laurence Gilbertson (Data Analyst, Contributor on 'Caldova Finance') receives Colin's email and registers the price
from the signed contract amendment. In this demo the contract and invoice data live in the lakehouse LH_CaldovaFinance
(Direct Lake model); at a customer they would live in the source database, e.g. Snowflake behind an Import or
DirectQuery semantic model. Copilot answers reflect the data from the last refresh of the semantic model, so the step
ends with a model refresh.

  --contract CTR-ANN-DE --price 4.45 --valid-from 2026-10-05
             Checks the change against the signed amendments (AMENDMENTS in scripts/generate_finance_data.py),
             reloads fin_contracts and fin_invoice_lines with the price registered, refreshes the model and validates
             both personas (Germany back to 100%). A change that doesn't match a signed amendment is refused.
  --reset    Back to the demo start: amendment not registered, Germany flagged again.

Usage:  pwsh -File scripts\\Update-CaldovaContractPrice.ps1 -Contract CTR-ANN-DE -UnitPrice 4.45 -ValidFrom 2026-10-05
        pwsh -File scripts\\Update-CaldovaContractPrice.ps1 -Reset
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import caldova_fabric as cf
import deploy_finance as fin

LOADED = {"fin_contracts", "fin_invoice_lines"}
GENERATOR = cf.ROOT / "scripts" / "generate_finance_data.py"


def log(msg: str) -> None:
    print(f"[contract-price] {msg}", flush=True)


def amendments() -> dict:
    spec = importlib.util.spec_from_file_location("generate_finance_data", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AMENDMENTS


def generate_registered() -> Path:
    out = Path(tempfile.mkdtemp(prefix="caldova-fin-registered-"))
    subprocess.run([sys.executable, str(GENERATOR), "--registered", "--registered-on", dt.date.today().isoformat(),
                    "--out", str(out)], check=True, capture_output=True, text=True)
    return out


def reload_model(state: dict, data_dir: Path) -> None:
    fin.step_load(state, data_dir=data_dir, only=LOADED)
    fin.step_refresh(state)
    fin.step_validate(state, data_dir=data_dir)


def update(state: dict, contract: str, price: Decimal, valid_from: dt.date) -> int:
    parts = contract.upper().split("-")
    amendment = amendments().get((parts[2], parts[1])) if len(parts) == 3 else None
    if amendment is None or amendment[0] != valid_from or Decimal(amendment[1]) != price:
        signed = f"${Decimal(amendment[1]):.2f} from {amendment[0]:%d %b %Y}" if amendment else "no signed amendment"
        log(f"{contract} ${price:.2f} from {valid_from:%d %b %Y} doesn't match the signed contract ({signed}): not applied")
        return 2
    log(f"{contract}: registering ${price:.2f} from {valid_from:%d %b %Y} (matches the signed amendment)")
    reload_model(state, generate_registered())
    log("done: the contract data holds the new price and the semantic model is refreshed; every report and Copilot "
        "answer uses it")
    return 0


def reset(state: dict) -> int:
    log("back to the demo start: amendment not registered ...")
    reload_model(state, fin.DATA)
    log("reset done: Germany flagged again")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--contract")
    ap.add_argument("--price", type=Decimal)
    ap.add_argument("--valid-from", type=dt.date.fromisoformat)
    ap.add_argument("--reset", action="store_true", help="back to the demo start state")
    args = ap.parse_args()
    if not args.reset and not (args.contract and args.price and args.valid_from):
        ap.error("give --contract, --price and --valid-from, or --reset")
    cf.guard_profile()
    log(f"signed in as {cf.signed_in_user()} (tenant {cf.CFG['tenantDomain']})")
    state = fin.load_state()
    missing = [k for k in ("dataWorkspaceId", "lakehouseId", "semanticModelId") if k not in state]
    if missing:
        raise SystemExit(f"Deployment state is missing {missing}: run Deploy-CaldovaFinance.ps1 first")
    return reset(state) if args.reset else update(state, args.contract, args.price, args.valid_from)


if __name__ == "__main__":
    sys.exit(main())
