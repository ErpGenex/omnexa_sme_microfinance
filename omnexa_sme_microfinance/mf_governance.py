# Copyright (c) 2026, ErpGenEx
"""MicroCapital governance — roles, workflow, SoD (world-class)."""

from __future__ import annotations

import frappe
from frappe import _

MF_ROLES: list[dict] = [
	{"role": "MF Field Officer", "desk_access": 1},
	{"role": "MF Branch Manager", "desk_access": 1},
	{"role": "MF Disbursement Officer", "desk_access": 1},
	{"role": "MF Collection Officer", "desk_access": 1},
	{"role": "MF Risk Analyst", "desk_access": 1},
]

ROLE_PERMISSIONS: list[dict] = [
	{"role": "MF Field Officer", "create": 1, "read": 1, "write": 1, "delete": 0, "submit": 0},
	{"role": "MF Branch Manager", "create": 0, "read": 1, "write": 1, "delete": 0, "submit": 1},
	{"role": "MF Disbursement Officer", "create": 0, "read": 1, "write": 1, "delete": 0, "submit": 1},
	{"role": "MF Collection Officer", "create": 0, "read": 1, "write": 1, "delete": 0, "submit": 0},
	{"role": "MF Risk Analyst", "create": 0, "read": 1, "write": 1, "delete": 0, "submit": 0},
	{"role": "Finance Microfinance Officer", "create": 1, "read": 1, "write": 1, "delete": 0, "submit": 1},
]


def ensure_mf_roles() -> list[str]:
	created: list[str] = []
	for spec in MF_ROLES:
		name = spec["role"]
		if not frappe.db.exists("Role", name):
			frappe.get_doc({"doctype": "Role", "role_name": name, "desk_access": spec["desk_access"]}).insert(
				ignore_permissions=True
			)
			created.append(name)
	return created


def _perm_row(role: str, p: dict) -> dict:
	submittable = bool(frappe.db.get_value("DocType", "Microfinance Case", "is_submittable"))
	row = {
		"role": role,
		"create": p.get("create", 0),
		"read": p.get("read", 1),
		"write": p.get("write", 0),
		"delete": p.get("delete", 0),
		"submit": p.get("submit", 0) if submittable else 0,
		"cancel": p.get("cancel", 0),
		"amend": 0,
		"report": 1,
		"export": 1,
		"print": 1,
		"email": 1,
		"share": 1,
	}
	return row


def sync_microfinance_case_permissions() -> None:
	if not frappe.db.exists("DocType", "Microfinance Case"):
		return
	meta = frappe.get_doc("DocType", "Microfinance Case")
	existing = {r.role: r for r in meta.permissions}
	for spec in ROLE_PERMISSIONS:
		row = _perm_row(spec["role"], spec)
		if spec["role"] in existing:
			doc = existing[spec["role"]]
			for k, v in row.items():
				if k != "role":
					setattr(doc, k, v)
		else:
			meta.append("permissions", row)
	meta.flags.ignore_permissions = True
	meta.save()
	frappe.clear_cache(doctype="Microfinance Case")


def enforce_sod_on_transition(doc, action: str) -> None:
	"""Block self-approval on sensitive workflow actions."""
	sensitive = {"Approve", "Disburse", "Close Case", "Risk Override"}
	if action not in sensitive:
		return
	if doc.owner == frappe.session.user and action in ("Approve", "Disburse"):
		frappe.throw(_("Segregation of Duties: you cannot {0} a case you created.").format(action))


def sync_mf_governance() -> dict:
	roles = ensure_mf_roles()
	from omnexa_core.omnexa_core.finance_demo.finance_vertical_bpe import sync_vertical_bpe

	out = sync_vertical_bpe("omnexa_sme_microfinance")
	return {"roles_created": roles, "workflow": out.get("workflow"), "stage_gate": True}
