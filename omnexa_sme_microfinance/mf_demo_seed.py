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


@frappe.whitelist()
def seed_microfinance_demo(company: str | None = None, branch: str | None = None) -> dict:
	company = company or frappe.defaults.get_user_default("Company")
	branch = branch or frappe.defaults.get_user_default("Branch")
	created = []
	for row in DEMO_GROUPS:
		if frappe.db.exists("Microfinance Case", {"group_name": row["group_name"]}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Microfinance Case",
				"group_name": row["group_name"],
				"member_count": row["member_count"],
				"principal": row["principal"],
				"term_months": 12,
				"group_maturity_cycles": 2,
				"collection_rate": 95,
				"lifecycle_stage": row["lifecycle_stage"],
				"company": company,
				"branch": branch,
			}
		)
		doc.insert(ignore_permissions=True)
		ws = row.get("workflow_state")
		if ws and doc.meta.get_field("workflow_state"):
			frappe.db.set_value("Microfinance Case", doc.name, "workflow_state", ws, update_modified=False)
		if row.get("docstatus") == 1:
			doc.reload()
			doc.docstatus = 1
			doc.save(ignore_permissions=True)
		created.append(doc.name)
	frappe.db.commit()
	return {"created": created, "count": len(created)}
