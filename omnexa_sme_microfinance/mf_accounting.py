# Copyright (c) 2026, ErpGenEx
"""MicroCapital disbursement accounting bridge (FinTruth Core)."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def create_disbursement_draft(doc) -> str | None:
	"""Create draft Payment Entry for group disbursement when company is set."""
	if not doc.company or not frappe.db.exists("DocType", "Payment Entry"):
		return None
	if doc.accounting_reference:
		return doc.accounting_reference
	try:
		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = "Pay"
		pe.party_type = "Supplier"
		pe.company = doc.company
		if doc.branch and pe.meta.get_field("branch"):
			pe.branch = doc.branch
		pe.posting_date = frappe.utils.today()
		pe.paid_amount = flt(doc.principal)
		pe.received_amount = flt(doc.principal)
		pe.mode_of_payment = "Cash"
		pe.remarks = f"MicroCapital disbursement — {doc.name} — {doc.group_name}"
		pe.insert(ignore_permissions=True)
		return pe.name
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"MicroCapital accounting draft {doc.name}")
		return f"DRAFT-REF-{doc.name}"
