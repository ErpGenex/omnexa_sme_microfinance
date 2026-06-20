# Copyright (c) 2026, ErpGenEx
"""MicroCapital Frappe Workflow — four/six eyes, delegation-ready."""

from __future__ import annotations

import frappe

WORKFLOW_NAME = "MicroCapital Group Lending"


def _ensure_workflow_state(state: str, style: str = "Primary") -> None:
	if frappe.db.exists("Workflow State", state):
		return
	frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state, "style": style}).insert(
		ignore_permissions=True
	)


def _ensure_workflow_action(action: str) -> None:
	if frappe.db.exists("Workflow Action Master", action):
		return
	frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
		ignore_permissions=True
	)


def _state(state, doc_status, *, allow_edit="All", update_field=None, update_value=None, style="Primary"):
	_ensure_workflow_state(state, style)
	row = {"state": state, "doc_status": str(doc_status), "style": style, "allow_edit": allow_edit}
	if update_field:
		row["update_field"] = update_field
		row["update_value"] = update_value
	return row


def _transition(state, action, next_state, allowed, *, self_approval=0):
	_ensure_workflow_action(action)
	return {
		"state": state,
		"action": action,
		"next_state": next_state,
		"allowed": allowed,
		"allow_self_approval": self_approval,
	}


def sync_microfinance_workflow() -> str:
	"""Legacy entry — delegates to universal 14-state stage-gate sync."""
	from omnexa_core.omnexa_core.finance_demo.finance_vertical_bpe import sync_vertical_bpe

	out = sync_vertical_bpe("omnexa_sme_microfinance")
	return out.get("workflow") or WORKFLOW_NAME
