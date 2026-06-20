# Copyright (c) 2026, ErpGenEx
from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime

from omnexa_sme_microfinance.engine.lifecycle import MicrofinanceCaseInput, evaluate_microfinance_lifecycle


class MicrofinanceCase(Document):
	def validate(self):
		self._apply_lifecycle_engine()
		self._sync_field_officer()
		self._set_sla_on_pending()
		self._guard_post_disbursement_edits()

	def before_submit(self):
		ws = getattr(self, "workflow_state", None) or ""
		allowed = ("Approved", "Completed", "Closed", "Disbursed", "In Collection")
		if ws and ws not in allowed:
			frappe.throw(_("Submit only after approval / disbursement workflow state."))

	def on_update(self):
		prev = self.get_doc_before_save()
		if not prev:
			return
		if self.lifecycle_stage == "Disbursement" and prev.lifecycle_stage != "Disbursement":
			from omnexa_sme_microfinance.mf_accounting import create_disbursement_draft

			ref = create_disbursement_draft(self)
			if ref:
				frappe.db.set_value("Microfinance Case", self.name, "accounting_reference", ref, update_modified=False)

	def _apply_lifecycle_engine(self) -> None:
		if not self.principal:
			return
		rate = Decimal(str(self.collection_rate or 95)) / Decimal("100")
		result = evaluate_microfinance_lifecycle(
			MicrofinanceCaseInput(
				principal=Decimal(str(self.principal)),
				term_months=int(self.term_months or 12),
				member_count=int(self.member_count or 5),
				group_maturity_cycles=int(self.group_maturity_cycles or 0),
				collection_rate=rate,
			)
		)
		self.risk_score = float(result.risk_score)
		self.recommended_stage = result.recommended_stage
		self.reason_codes = json.dumps(result.reason_codes)
		self.required_controls = json.dumps(result.required_controls)
		if not self.risk_band or self.is_new():
			self.risk_band = result.risk_band
		if self.lifecycle_stage == "Origination" and result.recommended_stage:
			# Advisory mapping — workflow drives transitions
			pass

	def _sync_field_officer(self) -> None:
		if not self.field_officer:
			self.field_officer = frappe.session.user

	def _set_sla_on_pending(self) -> None:
		ws = getattr(self, "workflow_state", None) or ""
		if ws in ("Pending Review", "Pending Approval", "Pending Verification") and not self.sla_due:
			self.sla_due = add_to_date(now_datetime(), hours=48)

	def _guard_post_disbursement_edits(self) -> None:
		if self.docstatus != 1:
			return
		prev = self.get_doc_before_save()
		if not prev or prev.docstatus != 1:
			return
		for field in ("principal", "member_count", "group_name"):
			if self.get(field) != prev.get(field):
				frappe.throw(_("Cannot change {0} after disbursement.").format(field))


def before_workflow_action(doc, action):
	from omnexa_sme_microfinance.mf_governance import enforce_sod_on_transition

	enforce_sod_on_transition(doc, action)
	if action == "Reject" and not doc.rejection_reason:
		frappe.msgprint(_("Consider documenting rejection_reason for audit trail."), indicator="orange")
