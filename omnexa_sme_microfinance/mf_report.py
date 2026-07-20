# Copyright (c) 2026, ErpGenEx
"""Microfinance Portfolio Overview — script report."""

from __future__ import annotations

import frappe


def ensure_microfinance_portfolio_report() -> str:
	name = "Microfinance Portfolio Overview"
	if frappe.db.exists("Report", name):
		return name
	report = frappe.get_doc(
		{
			"doctype": "Report",
			"report_name": name,
			"ref_doctype": "Microfinance Case",
			"report_type": "Script Report",
			"is_standard": "Yes",
			"module": "Omnexa SME Microfinance"
	}
	)
	report.insert(ignore_permissions=True)
	return name


def execute(filters=None):
	columns = [
		{"label": "Case", "fieldname": "name", "fieldtype": "Link", "options": "Microfinance Case", "width": 120
	},
		{"label": "Group", "fieldname": "group_name", "fieldtype": "Data", "width": 160
	},
		{"label": "Stage", "fieldname": "lifecycle_stage", "fieldtype": "Data", "width": 100
	},
		{"label": "Workflow", "fieldname": "workflow_state", "fieldtype": "Data", "width": 140
	},
		{"label": "Risk", "fieldname": "risk_band", "fieldtype": "Data", "width": 60
	},
		{"label": "Principal", "fieldname": "principal", "fieldtype": "Currency", "width": 110
	},
		{"label": "Members", "fieldname": "member_count", "fieldtype": "Int", "width": 80
	},
	]
	fields = ["name", "group_name", "lifecycle_stage", "risk_band", "principal", "member_count"]
	if frappe.get_meta("Microfinance Case").get_field("workflow_state"):
		fields.append("workflow_state")
	rows = frappe.get_all("Microfinance Case", fields=fields, order_by="modified desc", limit_page_length=500)
	return columns, rows
