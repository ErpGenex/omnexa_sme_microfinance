# Copyright (c) 2026, ErpGenEx
"""MicroCapital demo seed — cases across workflow stages."""

from __future__ import annotations

import frappe


DEMO_GROUPS: list[dict] = [
		{"group_name": "Demo Group Al-Nour", "member_count": 8, "principal": 45000, "lifecycle_stage": "Origination", "workflow_state": "Draft"},
	{"group_name": "Demo Group Al-Amal", "member_count": 6, "principal": 32000, "lifecycle_stage": "Origination", "workflow_state": "Submitted"},
	{"group_name": "Demo Group Al-Hayat", "member_count": 10, "principal": 60000, "lifecycle_stage": "Origination", "workflow_state": "In Progress"},
	{"group_name": "Demo Group Al-Rahma", "member_count": 7, "principal": 28000, "lifecycle_stage": "Disbursement", "workflow_state": "Completed", "docstatus": 1},
	{"group_name": "Demo Group Al-Salam", "member_count": 5, "principal": 22000, "lifecycle_stage": "Collection", "workflow_state": "Completed", "docstatus": 1},
	{"group_name": "Demo Group Al-Fajr", "member_count": 9, "principal": 55000, "lifecycle_stage": "Closed", "workflow_state": "Closed", "docstatus": 1},
]


def _seed_mf_group(row: dict, company: str | None, branch: str | None) -> str | None:
	if frappe.db.exists("Microfinance Case", {"group_name": row["group_name"]}):
		return None
	doc = frappe.get_doc(
		{
			"doctype": "Microfinance Case",
			"group_name": row["group_name"],
			"member_count": row["member_count"],
			"principal": row["principal"],
			"term_months": row.get("term_months", 12),
			"group_maturity_cycles": row.get("group_maturity_cycles", 2),
			"collection_rate": row.get("collection_rate", 95),
			"lifecycle_stage": row["lifecycle_stage"],
			"company": company,
			"branch": branch,
		}
	)
	doc.flags.ignore_branch_access = True
	doc.insert(ignore_permissions=True)
	ws = row.get("workflow_state")
	if ws and doc.meta.get_field("workflow_state"):
		frappe.db.set_value("Microfinance Case", doc.name, "workflow_state", ws, update_modified=False)
	if row.get("docstatus") == 1:
		doc.reload()
		doc.docstatus = 1
		doc.save(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def seed_microfinance_demo(company: str | None = None, branch: str | None = None) -> dict:
	company = company or frappe.defaults.get_user_default("Company")
	branch = branch or frappe.defaults.get_user_default("Branch")
	created = []
	for row in DEMO_GROUPS:
		name = _seed_mf_group(row, company, branch)
		if name:
			created.append(name)
	frappe.db.commit()
	return {"created": created, "count": len(created)}


def seed_microfinance_branch_demo(
	company: str | None = None,
	branch: str | None = None,
	groups: int = 50,
	force: int = 0,
	marker: str = "DEMO-FG",
) -> dict:
	"""Branch finance demo — scale MicroCapital groups across workflow stages."""
	from frappe.utils import cint

	company = company or frappe.defaults.get_user_default("Company")
	branch = branch or frappe.defaults.get_user_default("Branch")
	groups = max(1, min(cint(groups) or 50, 200))
	profile = [
		("Origination", "Draft", 0),
		("Origination", "Submitted", 0),
		("Origination", "In Progress", 0),
		("Disbursement", "Completed", 1),
		("Collection", "Completed", 1),
		("Closed", "Closed", 1),
	]
	if cint(force):
		for name in frappe.get_all(
			"Microfinance Case",
			filters={"group_name": ("like", f"{marker}%"), "company": company, "branch": branch},
			pluck="name",
		):
			try:
				doc = frappe.get_doc("Microfinance Case", name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Microfinance Case", name, force=1, ignore_permissions=True)
			except Exception:
				frappe.log_error(frappe.get_traceback(), f"mf_branch_demo_delete:{name}")
	elif frappe.db.count("Microfinance Case", {"group_name": ("like", f"{marker}%"), "company": company, "branch": branch}):
		count = frappe.db.count(
			"Microfinance Case", {"group_name": ("like", f"{marker}%"), "company": company, "branch": branch}
		)
		return {"ok": True, "app": "omnexa_sme_microfinance", "message": "already_seeded", "count": count}

	created = []
	for idx in range(1, groups + 1):
		lifecycle, wf, docstatus = profile[(idx - 1) % len(profile)]
		row = {
			"group_name": f"{marker} MF Group {idx:03d}",
			"member_count": 5 + (idx % 6),
			"principal": 15000 + (idx % 12) * 2500,
			"term_months": 12 + (idx % 3) * 6,
			"group_maturity_cycles": 1 + (idx % 3),
			"collection_rate": 88 + (idx % 12),
			"lifecycle_stage": lifecycle,
			"workflow_state": wf,
			"docstatus": docstatus,
		}
		name = _seed_mf_group(row, company, branch)
		if name:
			created.append(name)
	frappe.db.commit()
	return {"ok": True, "app": "omnexa_sme_microfinance", "created": created, "count": len(created)}
