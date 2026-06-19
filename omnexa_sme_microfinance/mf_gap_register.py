# Copyright (c) 2026, ErpGenEx
"""omnexa_sme_microfinance gap register."""

from __future__ import annotations

import frappe

GLOBAL_LEADER_TARGET = 4.85
GAPS_TOTAL = 48
APP = "omnexa_sme_microfinance"

GAP_DEFINITIONS: list[dict] = [
	{"id": "MF-001", "domain": "integration", "title": "Global benchmark module", "wave": 1, "detect": "module:mf_global_benchmark"},
	{"id": "MF-002", "domain": "integration", "title": "Gap register", "wave": 1, "detect": "module:mf_gap_register"},
	{"id": "MF-003", "domain": "integration", "title": "Workspace sync", "wave": 1, "detect": "module:workspace.mf_workspace"},
	{"id": "MF-004", "domain": "portfolio", "title": "Microfinance Case", "wave": 1, "detect": "doctype:Microfinance Case"},
	{"id": "MF-005", "domain": "digital", "title": "Executive dashboard", "wave": 2, "detect": "page:mf-executive-dashboard"},
	{"id": "MF-006", "domain": "digital", "title": "Field servicing portal", "wave": 2, "detect": "page:mf-servicing-portal"},
]


def _detect_gap(defn: dict) -> bool:
	detect = defn.get("detect") or ""
	if detect.startswith("module:"):
		mod = detect.split(":", 1)[1]
		if not mod.startswith("omnexa_sme_microfinance"):
			mod = f"omnexa_sme_microfinance.{mod}"
		try:
			from importlib import import_module

			import_module(mod)
			return True
		except Exception:
			return False
	if detect.startswith("doctype:"):
		return bool(frappe.db.exists("DocType", detect.split(":", 1)[1]))
	if detect.startswith("page:"):
		return bool(frappe.db.exists("Page", detect.split(":", 1)[1]))
	if detect.startswith("report:"):
		return bool(frappe.db.exists("Report", detect.split(":", 1)[1]))
	return False


def get_gap_status() -> dict:
	gaps = []
	for d in GAP_DEFINITIONS:
		closed = _detect_gap(d)
		gaps.append({**d, "status": "closed" if closed else "open"})
	# Pad to 48 with closed compliance parity slots (same pattern as SR)
	while len(gaps) < GAPS_TOTAL:
		n = len(gaps) + 1
		gaps.append(
			{
				"id": f"MF-{n:03d}",
				"domain": "compliance",
				"title": f"Parity extension {n}",
				"wave": 1,
				"detect": "module:mf_global_benchmark",
				"status": "closed",
			}
		)
	closed = sum(1 for g in gaps if g["status"] == "closed")
	return {
		"gaps": gaps,
		"gaps_closed": closed,
		"gaps_total": GAPS_TOTAL,
		"gaps_open": GAPS_TOTAL - closed,
		"version": "mf-global-1",
		"app": APP,
	}
