# Copyright (c) 2026, ErpGenEx
"""SME Microfinance workspace — full sidebar catalog (vertical-owned)."""

from __future__ import annotations

import json

import frappe

from omnexa_core.omnexa_core.vertical_workspace_sync import (
	build_link_rows_for_app,
	drop_missing_workspace_dashboard_links,
)

WORKSPACE_NAME = "SME Microfinance"
_SHORTCUT_COLORS = ("Blue", "Green", "Orange", "Red", "Cyan", "Purple", "Teal", "Pink", "Yellow")

WORKSPACE_SECTIONS: list[tuple[str, list[tuple[str, str, str]]]] = [
	(
		"📊 Dashboards",
		[
			("Page", "mf-executive-dashboard", "Executive Dashboard"),
			("Page", "mf-servicing-portal", "Field Portal"),
			("Page", "finance-demo-hub", "Finance Demo Hub"),
		],
	),
	(
		"🤝 Micro portfolio",
		[
			("DocType", "Microfinance Case", "Micro Case"),
		],
	),
	(
		"💰 Finance",
		[
			("DocType", "Journal Entry", "Journal Entry"),
			("DocType", "Payment Entry", "Payment Entry"),
		],
	),
]


def _sanitize_link_rows(rows: list[dict]) -> list[dict]:
	out: list[dict] = []
	for row in rows:
		if row.get("type") != "Link":
			out.append(row)
			continue
		ref = row.get("report_ref_doctype")
		if ref and not frappe.db.exists("DocType", ref):
			continue
		out.append(row)
	return out


def _build_link_rows() -> list[dict]:
	return _sanitize_link_rows(build_link_rows_for_app("omnexa_sme_microfinance", WORKSPACE_SECTIONS))


def _build_shortcuts(link_rows: list[dict]) -> list[dict]:
	shortcuts: list[dict] = []
	idx = 0
	for lt in ("Page", "DocType", "Report"):
		for row in link_rows:
			if row.get("type") != "Link" or row.get("link_type") != lt:
				continue
			entry = {
				"label": row["label"],
				"link_to": row["link_to"],
				"type": row["link_type"],
				"color": _SHORTCUT_COLORS[idx % len(_SHORTCUT_COLORS)],
			}
			if lt == "DocType":
				entry["doc_view"] = "List"
			shortcuts.append(entry)
			idx += 1
	return shortcuts


def sync_mf_workspace_menu(*, save: bool = True) -> dict:
	stats = {"sections": 0, "links": 0, "shortcuts": 0}
	if not frappe.db.exists("Workspace", WORKSPACE_NAME):
		from omnexa_core.omnexa_core.workspace_control_tower import sync_workspace_for_app

		sync_workspace_for_app("omnexa_sme_microfinance")
	rows = _build_link_rows()
	link_rows = [r for r in rows if r.get("type") == "Link"]
	ws = frappe.get_doc("Workspace", WORKSPACE_NAME)
	ws.set("links", [])
	ws.set("shortcuts", [])
	for row in rows:
		if row["type"] == "Card Break":
			stats["sections"] += 1
		else:
			stats["links"] += 1
		ws.append("links", row)
	for sc in _build_shortcuts(rows):
		ws.append("shortcuts", sc)
	stats["shortcuts"] = len(ws.shortcuts)
	drop_missing_workspace_dashboard_links(ws)
	if save:
		ws.flags.ignore_permissions = True
		ws.save()
		frappe.clear_cache(doctype="Workspace")
	stats["total_links"] = len(link_rows)
	return stats


def sync_mf_workspace() -> str:
	from omnexa_core.omnexa_core.workspace_control_tower import sync_workspace_for_app

	sync_workspace_for_app("omnexa_sme_microfinance")
	sync_mf_workspace_menu()
	return WORKSPACE_NAME
